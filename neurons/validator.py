"""
StoryFi Bittensor Validator
============================

This validator:
1. Generates tasks for miners
2. Queries miners with different task types
3. Evaluates responses using scoring system
4. Calculates and sets weights on-chain
5. Implements anti-cheating mechanisms

Usage:
    python neurons/validator.py \
        --netuid 42 \
        --wallet.name my_validator \
        --wallet.hotkey default \
        --logging.info
"""

import argparse
import asyncio
import json
import os
import random
import sys
import time
import traceback
from collections import deque
from typing import Dict, Any, List, Tuple, Optional

import bittensor as bt
import torch
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from template.protocol import (
    StoryGenerationSynapse,
    create_blueprint_synapse,
    create_characters_synapse,
    create_story_arc_synapse,
    create_chapters_synapse
)
from template.utils import (
    Timer,
    exponential_moving_average,
    normalize_weights
)
from scoring import (
    calculate_technical_score,
    calculate_structure_score,
    calculate_content_score
)

# Load environment variables
load_dotenv()


class StoryValidator:
    """
    StoryFi Validator that evaluates miners and distributes rewards.

    The validator:
    1. Periodically queries miners with story generation tasks
    2. Scores responses using 3-part system (Technical + Structure + Content)
    3. Updates EMA scores and calculates weights
    4. Sets weights on-chain every N queries
    5. Detects and blacklists cheating miners
    """

    def __init__(self, config: bt.config):
        """Initialize the validator."""
        self.config = config
        bt.logging.info("Initializing StoryFi Validator...")

        # Initialize Bittensor components
        self.wallet = bt.wallet(config=self.config)
        self.subtensor = bt.subtensor(config=self.config)
        self.metagraph = bt.metagraph(netuid=self.config.netuid, network=self.subtensor.network)
        self.dendrite = bt.dendrite(wallet=self.wallet)

        # Configuration
        self.query_interval = int(os.getenv("VALIDATOR_QUERY_INTERVAL", "12"))
        self.timeout = int(os.getenv("VALIDATOR_TIMEOUT", "60"))
        self.ema_alpha = float(os.getenv("EMA_ALPHA", "0.1"))
        self.temperature = float(os.getenv("SOFTMAX_TEMPERATURE", "2.0"))
        self.weight_update_frequency = int(os.getenv("WEIGHT_UPDATE_FREQ", "100"))

        # Task distribution (blueprint:40%, characters:25%, story_arc:25%, chapters:10%)
        self.task_distribution = {
            "blueprint": 0.40,
            "characters": 0.25,
            "story_arc": 0.25,
            "chapters": 0.10
        }

        # State
        self.scores = {}  # {miner_uid: ema_score}
        self.history = deque(maxlen=1000)  # Historical responses for plagiarism detection
        self.blacklist = set()  # Blacklisted miner UIDs
        self.violations = {}  # {miner_uid: violation_count}

        # Statistics
        self.total_queries = 0
        self.successful_queries = 0
        self.total_rewards = 0.0

        # Sample data for task generation
        self.sample_prompts = [
            "一个关于赛博朋克黑客的故事",
            "一个关于太空探险的故事",
            "一个古代武侠传奇故事",
            "一个末日生存的故事",
            "一个都市悬疑推理故事",
            "一个奇幻魔法世界的故事",
            "一个时间旅行的故事",
            "一个AI觉醒的故事"
        ]

        bt.logging.info(f"✅ Wallet: {self.wallet.hotkey.ss58_address}")
        bt.logging.info(f"✅ Netuid: {self.config.netuid}")
        bt.logging.info(f"✅ Query interval: {self.query_interval}s")

    def select_task_type(self) -> str:
        """Randomly select a task type based on distribution."""
        return random.choices(
            list(self.task_distribution.keys()),
            weights=list(self.task_distribution.values())
        )[0]

    def create_task(self, task_type: str) -> Tuple[StoryGenerationSynapse, Dict[str, Any]]:
        """
        Create a task synapse with mock context.

        Args:
            task_type: Type of task to create

        Returns:
            Tuple of (synapse, context)
        """
        user_input = random.choice(self.sample_prompts)
        context = {"user_input": user_input}

        if task_type == "blueprint":
            synapse = create_blueprint_synapse(user_input)

        elif task_type == "characters":
            # Mock blueprint for characters task
            mock_blueprint = {
                "title": "测试故事",
                "genre": "科幻",
                "setting": "未来世界",
                "core_conflict": "人与AI的冲突",
                "themes": ["科技", "伦理"],
                "tone": "紧张",
                "target_audience": "成人"
            }
            synapse = create_characters_synapse(mock_blueprint, user_input)
            context["blueprint"] = mock_blueprint

        elif task_type == "story_arc":
            # Mock blueprint and characters
            mock_blueprint = {
                "title": "测试故事",
                "genre": "科幻",
                "setting": "未来世界",
                "core_conflict": "人与AI的冲突",
                "themes": ["科技", "伦理"],
                "tone": "紧张",
                "target_audience": "成人"
            }
            mock_characters = {
                "characters": [
                    {"id": "protagonist", "name": "主角", "archetype": "英雄"},
                    {"id": "ally", "name": "盟友", "archetype": "助手"},
                    {"id": "rival", "name": "对手", "archetype": "反派"},
                    {"id": "mentor", "name": "导师", "archetype": "智者"},
                    {"id": "wildcard", "name": "变数", "archetype": "神秘人"}
                ]
            }
            synapse = create_story_arc_synapse(mock_blueprint, mock_characters, user_input)
            context["blueprint"] = mock_blueprint
            context["characters"] = mock_characters

        elif task_type == "chapters":
            # Mock complete context
            mock_blueprint = {"title": "测试故事"}
            mock_characters = {"characters": []}
            mock_story_arc = {
                "title": "测试故事",
                "chapters": [{"id": i} for i in range(1, 13)]
            }
            chapter_ids = [1]  # v3.0.0: 使用整数而不是字符串
            synapse = create_chapters_synapse(
                mock_blueprint, mock_characters, mock_story_arc,
                chapter_ids, user_input
            )
            context["blueprint"] = mock_blueprint
            context["characters"] = mock_characters
            context["story_arc"] = mock_story_arc

        return synapse, context

    async def query_miners(
        self,
        synapse: StoryGenerationSynapse,
        miners: List[bt.AxonInfo]
    ) -> List[StoryGenerationSynapse]:
        """
        Query multiple miners with a task.

        Args:
            synapse: Task synapse
            miners: List of miner axons

        Returns:
            List of responses
        """
        try:
            responses = await self.dendrite.forward(
                axons=miners,
                synapse=synapse,
                timeout=self.timeout
            )
            return responses
        except Exception as e:
            bt.logging.error(f"Error querying miners: {e}")
            return [synapse] * len(miners)  # Return empty responses on error

    def score_response(
        self,
        response: StoryGenerationSynapse,
        context: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Score a miner's response using 3-part scoring system (Protocol v3.0.0).

        Args:
            response: Miner's response synapse
            context: Task context

        Returns:
            Tuple of (total_score, breakdown)
        """
        # Initialize breakdown
        breakdown = {
            "technical": 0.0,
            "structure": 0.0,
            "content": 0.0,
            "total": 0.0
        }

        # Get output data (v3.0.0: direct Dict access)
        data = response.output_data
        if not data:
            return 0.0, breakdown

        # Get required fields
        required_fields = response.get_required_output_fields()

        # 1. Technical Score (30 points)
        # v3.0.0: convert output_data to JSON string for technical scoring
        output_json_str = json.dumps(data, ensure_ascii=False)
        tech_score, tech_breakdown = calculate_technical_score(
            output_json_str,
            response.generation_time,
            response.task_type,
            required_fields
        )
        breakdown["technical"] = tech_score
        breakdown["technical_breakdown"] = tech_breakdown

        # 2. Structure Score (40 points)
        struct_score, struct_breakdown = calculate_structure_score(
            data,
            response.task_type
        )
        breakdown["structure"] = struct_score
        breakdown["structure_breakdown"] = struct_breakdown

        # 3. Content Score (30 points)
        content_score, content_breakdown = calculate_content_score(
            data,
            context,
            response.task_type,
            history=[h["output_data"] for h in list(self.history)[-20:]],
            use_embeddings=False  # Set to True when OpenAI embeddings are available
        )
        breakdown["content"] = content_score
        breakdown["content_breakdown"] = content_breakdown

        # Total score (0-100)
        total = tech_score + struct_score + content_score
        breakdown["total"] = total

        return total, breakdown

    def detect_plagiarism(
        self,
        response: StoryGenerationSynapse,
        all_responses: List[StoryGenerationSynapse]
    ) -> Tuple[bool, str, float]:
        """
        Detect plagiarism in response (Protocol v3.0.0).

        Args:
            response: Current response to check
            all_responses: All responses in current batch

        Returns:
            Tuple of (is_plagiarism, type, similarity)
        """
        # First check if response is None or doesn't have output_data
        if response is None or not hasattr(response, 'output_data'):
            return False, "", 0.0

        current_data = response.output_data
        if not current_data:
            return False, "", 0.0

        # Check against current batch (cross-miner copying)
        for other in all_responses:
            if other == response:
                continue

            # Skip if other response is None or invalid
            if other is None or not hasattr(other, 'output_data'):
                continue

            other_data = other.output_data
            if not other_data:
                continue

            similarity = self.calculate_similarity(current_data, other_data)

            if similarity > 0.95:
                return True, "cross_miner_copy", similarity

        # Check against history (template reuse)
        for historical in list(self.history)[-50:]:
            historical_data = historical.get("output_data")
            if not historical_data:
                continue

            similarity = self.calculate_similarity(current_data, historical_data)

            if similarity > 0.90:
                return True, "template_reuse", similarity

        return False, "original", 0.0

    def calculate_similarity(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> float:
        """Calculate simple similarity between two data objects."""
        str1 = json.dumps(data1, ensure_ascii=False, sort_keys=True)
        str2 = json.dumps(data2, ensure_ascii=False, sort_keys=True)

        # Character-level bigrams
        def get_bigrams(s: str) -> set:
            return set(s[i:i+2] for i in range(len(s) - 1))

        bigrams1 = get_bigrams(str1)
        bigrams2 = get_bigrams(str2)

        if not bigrams1 or not bigrams2:
            return 0.0

        intersection = len(bigrams1 & bigrams2)
        union = len(bigrams1 | bigrams2)

        return intersection / union if union > 0 else 0.0

    def update_ema_scores(self, new_scores: Dict[int, float]):
        """Update EMA scores for miners."""
        for uid, score in new_scores.items():
            if uid not in self.scores:
                self.scores[uid] = score
            else:
                self.scores[uid] = exponential_moving_average(
                    score,
                    self.scores[uid],
                    self.ema_alpha
                )

    def calculate_weights(self) -> Dict[int, float]:
        """
        Calculate weights using 3-factor system (inspired by SoulX):
        - 15% Stake weight (防止新矿工作弊)
        - 75% Quality score (当前表现)
        - 10% Historical score (长期稳定性)
        """
        if not self.scores:
            return {}

        # Calculate composite scores with stake consideration
        composite_scores = {}

        for uid, quality_score in self.scores.items():
            # 1. Get stake weight
            try:
                stake = self.metagraph.S[uid].item()
                max_stake = max(self.metagraph.S).item() if len(self.metagraph.S) > 0 else 1.0
                stake_weight = stake / max_stake if max_stake > 0 else 0.0
            except Exception as e:
                bt.logging.warning(f"Failed to get stake for UID {uid}: {e}")
                stake_weight = 0.0

            # 2. Get historical score (从历史记录计算平均)
            historical_scores = [
                h["score"] for h in list(self.history)[-50:]
                if h.get("uid") == uid
            ]
            historical_avg = (
                sum(historical_scores) / len(historical_scores)
                if historical_scores else quality_score
            )
            historical_score = historical_avg / 100.0  # Normalize to 0-1

            # 3. Normalize quality score to 0-1
            normalized_quality = quality_score / 100.0

            # 4. Composite score (15% stake + 75% quality + 10% history)
            composite = (
                0.15 * stake_weight +
                0.75 * normalized_quality +
                0.10 * historical_score
            )

            composite_scores[uid] = composite

        # Apply temperature (增加竞争差异)
        incentives = {
            uid: score ** self.temperature
            for uid, score in composite_scores.items()
        }

        # Normalize
        weights = normalize_weights(incentives)

        # Apply minimum weight (防止完全归零)
        min_weight = 0.001
        weights = {uid: max(w, min_weight) for uid, w in weights.items()}

        # Re-normalize
        weights = normalize_weights(weights)

        return weights

    async def set_weights(self):
        """Set weights on blockchain."""
        try:
            weights_dict = self.calculate_weights()

            if not weights_dict:
                bt.logging.warning("No weights to set")
                return

            # Convert to lists
            uids = list(weights_dict.keys())
            weights = [weights_dict[uid] for uid in uids]

            # Convert to tensors
            uids_tensor = torch.tensor(uids, dtype=torch.int64)
            weights_tensor = torch.tensor(weights, dtype=torch.float32)

            # Set weights
            success, message = self.subtensor.set_weights(
                netuid=self.config.netuid,
                wallet=self.wallet,
                uids=uids_tensor,
                weights=weights_tensor,
                wait_for_inclusion=False,
                wait_for_finalization=False
            )

            if success:
                bt.logging.success(f"✅ Weights set: {len(uids)} miners")
            else:
                bt.logging.error(f"❌ Failed to set weights: {message}")

        except Exception as e:
            bt.logging.error(f"Error setting weights: {e}")
            bt.logging.error(traceback.format_exc())

    async def run_step(self):
        """Run one validation step."""
        try:
            # 1. Select task type
            task_type = self.select_task_type()
            bt.logging.info(f"🎯 Task type: {task_type}")

            # 2. Create task
            synapse, context = self.create_task(task_type)

            # 3. Select miners (top 70% + random 30%)
            all_miners = self.metagraph.axons
            available_miners = [
                (i, axon) for i, axon in enumerate(all_miners)
                if i not in self.blacklist
            ]

            if not available_miners:
                bt.logging.warning("No available miners")
                await asyncio.sleep(self.query_interval)
                return

            # Select top performers + random exploration
            num_miners = min(10, len(available_miners))
            sorted_miners = sorted(
                available_miners,
                key=lambda x: self.scores.get(x[0], 0),
                reverse=True
            )

            top_k = int(num_miners * 0.7)
            explore_k = num_miners - top_k

            selected = sorted_miners[:top_k]
            if len(sorted_miners) > top_k:
                selected += random.sample(sorted_miners[top_k:], min(explore_k, len(sorted_miners) - top_k))

            selected_uids = [uid for uid, _ in selected]
            selected_axons = [axon for _, axon in selected]

            bt.logging.info(f"📡 Querying {len(selected_axons)} miners: {selected_uids}")

            # 4. Query miners
            with Timer() as t:
                responses = await self.query_miners(synapse, selected_axons)

            bt.logging.info(f"⏱️  Query completed in {t.elapsed:.2f}s")

            # 5. Score responses
            scores = {}
            for uid, response in zip(selected_uids, responses):
                # Skip if response is None or invalid
                if response is None or not hasattr(response, 'output_data'):
                    bt.logging.warning(f"⚠️  Miner {uid}: Invalid response")
                    scores[uid] = 0.0
                    continue

                # Check plagiarism
                is_plagiarism, plag_type, similarity = self.detect_plagiarism(response, responses)

                if is_plagiarism:
                    bt.logging.warning(f"⚠️  Miner {uid}: Plagiarism detected ({plag_type}, similarity={similarity:.2f})")
                    self.violations[uid] = self.violations.get(uid, 0) + 1

                    if self.violations[uid] >= 3:
                        self.blacklist.add(uid)
                        bt.logging.error(f"🚫 Miner {uid} blacklisted (3 violations)")

                    scores[uid] = 0.0
                    continue

                # Score response
                score, breakdown = self.score_response(response, context)
                scores[uid] = score

                bt.logging.info(
                    f"📊 Miner {uid}: {score:.2f} points "
                    f"(tech={breakdown['technical']:.1f}, "
                    f"struct={breakdown['structure']:.1f}, "
                    f"content={breakdown['content']:.1f})"
                )

                # Record history (v3.0.0: store output_data instead of output_json)
                self.history.append({
                    "uid": uid,
                    "task_type": task_type,
                    "output_data": response.output_data,
                    "score": score,
                    "timestamp": time.time()
                })

            # 6. Update EMA scores
            self.update_ema_scores(scores)

            # 7. Update statistics
            self.total_queries += 1
            self.successful_queries += len([s for s in scores.values() if s > 0])
            self.total_rewards += sum(scores.values())

            # 8. Set weights periodically
            if self.total_queries % self.weight_update_frequency == 0:
                await self.set_weights()

        except Exception as e:
            bt.logging.error(f"Error in run_step: {e}")
            bt.logging.error(traceback.format_exc())

    async def run(self):
        """Main run loop."""
        bt.logging.info("🚀 Starting validator...")

        # Sync metagraph
        self.metagraph.sync(subtensor=self.subtensor)
        bt.logging.info(f"📡 Metagraph synced: {len(self.metagraph.axons)} miners")

        try:
            while True:
                await self.run_step()

                # Print statistics
                if self.total_queries % 10 == 0:
                    avg_score = (
                        self.total_rewards / self.successful_queries
                        if self.successful_queries > 0
                        else 0.0
                    )

                    bt.logging.info(
                        f"\n📈 Statistics:\n"
                        f"  Total queries: {self.total_queries}\n"
                        f"  Successful: {self.successful_queries}\n"
                        f"  Avg score: {avg_score:.2f}\n"
                        f"  Blacklisted: {len(self.blacklist)}\n"
                        f"  Active miners: {len(self.scores)}"
                    )

                # Sync metagraph periodically
                if self.total_queries % 100 == 0:
                    self.metagraph.sync(subtensor=self.subtensor)

                # Wait before next query
                await asyncio.sleep(self.query_interval)

        except KeyboardInterrupt:
            bt.logging.info("🛑 Shutting down validator...")

            # Final weight update
            await self.set_weights()


def get_config():
    """Get configuration from command line arguments."""
    parser = argparse.ArgumentParser()

    # Add Bittensor standard arguments
    bt.subtensor.add_args(parser)
    bt.wallet.add_args(parser)
    bt.logging.add_args(parser)

    # Add custom arguments
    parser.add_argument("--netuid", type=int, default=42, help="Subnet netuid")

    # Parse and add bittensor config
    config = bt.config(parser)

    return config


def main():
    """Main entry point."""
    config = get_config()

    # Setup logging
    bt.logging.set_trace(config.logging.debug)
    bt.logging.set_debug(config.logging.debug)
    bt.logging.set_info(config.logging.info)

    # Create and run validator
    validator = StoryValidator(config)
    asyncio.run(validator.run())


if __name__ == "__main__":
    main()
