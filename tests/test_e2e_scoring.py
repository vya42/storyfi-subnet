#!/usr/bin/env python3
"""
End-to-End Scoring Test
=======================

This test simulates the complete scoring flow:
1. Miner generates story content
2. Validator scores the response using all 4 scoring modules
3. Verify total score calculation

Run with:
    ZHIPU_API_KEY=xxx python3 tests/test_e2e_scoring.py
"""

import sys
import os
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoring import (
    calculate_technical_score,
    calculate_structure_score,
    calculate_content_score,
    calculate_narrative_score
)


def simulate_miner_response(task_type: str, quality: str = "good"):
    """
    Simulate a miner's response.

    Args:
        task_type: "blueprint", "characters", "story_arc", "chapters"
        quality: "good", "average", "poor"
    """
    if task_type == "blueprint":
        if quality == "good":
            return {
                "title": "星际迷途：最后的希望",
                "genre": "科幻冒险",
                "setting": "2150年，人类已经建立了横跨三个星系的殖民帝国。边缘星球资源匮乏但自由度高，主角在这里经营一家小型货运公司。帝国的铁腕统治让边缘地带成为流亡者和梦想家的天堂。",
                "core_conflict": "一艘载有远古外星文明遗物的飞船坠落在主角的星球上，这些遗物可能改变人类的命运。帝国军队、海盗势力和神秘的外星追踪者都在寻找它，主角必须在保护家园和追寻真相之间做出抉择。",
                "themes": ["探索未知", "自由与秩序", "牺牲与救赎", "人性本质"],
                "tone": "史诗感与个人冒险并重，紧张刺激中带有深度思考",
                "target_audience": "18-35岁科幻爱好者"
            }
        elif quality == "average":
            return {
                "title": "太空冒险",
                "genre": "科幻",
                "setting": "未来的太空，有很多星球",
                "core_conflict": "主角要完成一个任务",
                "themes": ["冒险", "友情"],
                "tone": "紧张",
                "target_audience": "年轻人"
            }
        else:  # poor
            return {
                "title": "故事",
                "genre": "科幻",
                "setting": "太空",
                "core_conflict": "打架",
                "themes": ["好"],
                "tone": "一般",
                "target_audience": "人"
            }

    elif task_type == "characters":
        if quality == "good":
            return {
                "characters": [
                    {
                        "id": "char_001",
                        "name": "林远星",
                        "archetype": "不情愿的英雄",
                        "background": "前帝国飞行员，因拒绝执行屠杀平民的命令而被流放到边缘星球。他失去了一切，只剩下一艘破旧的货船和对自由的渴望。五年的流放生活让他学会了低调，但内心的正义感从未消失。",
                        "motivation": "保护新家园的人们，同时找到自我救赎的道路。他想证明自己当初的选择是对的。",
                        "skills": ["星际导航", "近身格斗", "机械维修", "谈判"],
                        "personality_traits": ["沉默寡言", "正义感强", "内心孤独", "值得信赖"],
                        "relationships": {
                            "char_002": "信任的伙伴",
                            "char_003": "复杂的过去"
                        }
                    },
                    {
                        "id": "char_002",
                        "name": "艾拉",
                        "archetype": "神秘向导",
                        "background": "外星飞船中唯一幸存的乘客，来自一个即将灭绝的古老种族。她携带着种族最后的希望——一份可以改变银河格局的知识。",
                        "motivation": "寻找新的家园，同时帮助人类避免重蹈她的种族覆辙。",
                        "skills": ["心灵感应", "高级科技操作", "多语言交流", "历史知识"],
                        "personality_traits": ["温和但坚定", "智慧", "略带悲伤", "神秘"],
                        "relationships": {
                            "char_001": "依赖的保护者"
                        }
                    }
                ]
            }
        else:
            return {
                "characters": [
                    {"id": "1", "name": "主角", "background": "普通人"}
                ]
            }

    elif task_type == "story_arc":
        if quality == "good":
            return {
                "chapters": [
                    {"chapter": 1, "title": "坠落的星辰", "description": "外星飞船坠落，打破边缘星球的平静", "storyProgress": 5},
                    {"chapter": 2, "title": "意外的相遇", "description": "林远星发现艾拉，两人命运交织", "storyProgress": 12},
                    {"chapter": 3, "title": "追踪者", "description": "帝国军队和神秘势力开始追踪", "storyProgress": 20},
                    {"chapter": 4, "title": "逃离", "description": "主角团队被迫逃离家园", "storyProgress": 28},
                    {"chapter": 5, "title": "揭示", "description": "艾拉透露遗物的真正力量", "storyProgress": 35},
                    {"chapter": 6, "title": "联盟", "description": "寻找潜在盟友对抗帝国", "storyProgress": 42},
                    {"chapter": 7, "title": "背叛", "description": "盟友中出现叛徒", "storyProgress": 50},
                    {"chapter": 8, "title": "低谷", "description": "团队遭受重大损失", "storyProgress": 58},
                    {"chapter": 9, "title": "真相", "description": "发现帝国背后的秘密", "storyProgress": 67},
                    {"chapter": 10, "title": "反击", "description": "制定最终计划", "storyProgress": 78},
                    {"chapter": 11, "title": "决战", "description": "与帝国正面对决", "storyProgress": 90},
                    {"chapter": 12, "title": "新的开始", "description": "胜利后的重建与希望", "storyProgress": 100}
                ],
                "arcs": {
                    "act1": {"chapters": [1, 2, 3], "theme": "建立"},
                    "act2a": {"chapters": [4, 5, 6], "theme": "上升"},
                    "act2b": {"chapters": [7, 8, 9], "theme": "危机"},
                    "act3": {"chapters": [10, 11, 12], "theme": "解决"}
                }
            }
        else:
            return {
                "chapters": [
                    {"chapter": 1, "title": "开始", "storyProgress": 50},
                    {"chapter": 2, "title": "结束", "storyProgress": 100}
                ]
            }

    elif task_type == "chapters":
        if quality == "good":
            return {
                "chapters": [
                    {
                        "chapter": 1,
                        "title": "坠落的星辰",
                        "content": """
夜空中划过一道炽烈的光芒，比任何流星都要明亮百倍。

林远星放下手中的扳手，从破旧货船"流浪者号"的引擎舱中探出头来。在这个被帝国遗忘的边缘星球——新望镇，他已经习惯了寂静的夜晚。只有偶尔路过的走私船和远处矿场的轰鸣声打破这份宁静。

但今晚不同。

那道光芒没有消失，反而越来越近。他能感受到空气中弥漫的臭氧味，能听到远处传来的低沉轰鸣。地面开始轻微震颤，货船的警报系统疯狂尖叫起来。

"那不是陨石，"他自言自语，眼睛紧盯着逐渐清晰的轮廓，"那是...一艘飞船。"

飞船——如果还能这么称呼的话——正以惊人的速度坠向地面。它的外形不像任何人类设计，流线型的轮廓带着一种诡异的美感。燃烧的尾焰拖出一条几十公里长的烟道，像是神明划过天际的手指。

坠落点距离他的小镇不到十公里。林远星知道，无论那是什么，帝国的探测器很快就会发现它。边缘星球虽然偏远，但帝国的监控网络无处不在。

他有两个选择：假装什么都没看到，继续过他平静的流放生活；或者赶在帝国军队到来之前，去看看那艘飞船里到底有什么。

他想起了五年前那个改变他一生的夜晚。想起了那些无辜的面孔——老人、妇女、孩子——他们恐惧的眼神。想起了自己违抗命令的那一刻，想起了军事法庭上的判决。

"该死的，"他抓起一把激光手枪，朝着坠落点跑去，"我就不能安安静静地当个修理工吗？"

流浪者号的引擎轰鸣着启动。林远星驾驶着他破旧的货船，朝着那团还在冒烟的残骸飞去。
                        """,
                        "choices": [
                            {
                                "text": "悄悄接近飞船残骸",
                                "consequences": {"stealth": 1, "discovery": "partial"},
                                "next_chapter": 2
                            },
                            {
                                "text": "先返回镇上召集帮手",
                                "consequences": {"allies": 1, "time_lost": 1},
                                "next_chapter": 2
                            },
                            {
                                "text": "发出求救信号",
                                "consequences": {"attention": "high", "help": "uncertain"},
                                "next_chapter": 2
                            }
                        ]
                    }
                ]
            }
        else:
            return {
                "chapters": [
                    {
                        "chapter": 1,
                        "title": "开始",
                        "content": "故事开始了。主角出发。",
                        "choices": [{"text": "继续"}]
                    }
                ]
            }


def calculate_full_score(data, context, task_type, generation_time=5.0):
    """
    Calculate full score using all 4 scoring modules.

    This mirrors the validator's scoring logic.
    """
    breakdown = {}

    # Get required fields based on task type
    required_fields = {
        "blueprint": ["title", "genre", "setting", "core_conflict", "themes"],
        "characters": ["characters"],
        "story_arc": ["chapters"],
        "chapters": ["chapters"]
    }.get(task_type, [])

    # 1. Technical Score (20 points)
    output_json_str = json.dumps(data, ensure_ascii=False)
    tech_score_raw, tech_breakdown = calculate_technical_score(
        output_json_str,
        generation_time,
        task_type,
        required_fields
    )
    tech_score = tech_score_raw * (20.0 / 30.0)
    breakdown["technical"] = tech_score
    breakdown["technical_breakdown"] = tech_breakdown

    # 2. Structure Score (30 points)
    struct_score_raw, struct_breakdown = calculate_structure_score(
        data,
        task_type
    )
    struct_score = struct_score_raw * (30.0 / 40.0)
    breakdown["structure"] = struct_score
    breakdown["structure_breakdown"] = struct_breakdown

    # 3. Content Score (20 points)
    content_score_raw, content_breakdown = calculate_content_score(
        data,
        context,
        task_type,
        history=[],
        use_embeddings=False
    )
    content_score = content_score_raw * (20.0 / 30.0)
    breakdown["content"] = content_score
    breakdown["content_breakdown"] = content_breakdown

    # 4. Narrative Merit Score (30 points) - AI评分
    narrative_score, narrative_breakdown = calculate_narrative_score(
        data,
        context,
        task_type
    )
    breakdown["narrative"] = narrative_score
    breakdown["narrative_breakdown"] = narrative_breakdown

    # Total score
    total_score = tech_score + struct_score + content_score + narrative_score
    breakdown["total"] = total_score

    return total_score, breakdown


def run_e2e_test():
    """Run end-to-end scoring test."""
    print("=" * 70)
    print("StoryNet End-to-End Scoring Test")
    print("=" * 70)

    # Check API key
    if not os.getenv("ZHIPU_API_KEY"):
        print("\n⚠️  ZHIPU_API_KEY not set. AI scoring will use fallback.")
        print("   Set it with: export ZHIPU_API_KEY=xxx")

    results = []

    # Test each task type with different quality levels
    test_cases = [
        ("blueprint", "good"),
        ("blueprint", "poor"),
        ("characters", "good"),
        ("story_arc", "good"),
        ("chapters", "good"),
        ("chapters", "poor"),
    ]

    for task_type, quality in test_cases:
        print(f"\n{'=' * 70}")
        print(f"Test: {task_type.upper()} ({quality} quality)")
        print("=" * 70)

        # Simulate miner response
        data = simulate_miner_response(task_type, quality)
        context = {"user_input": "写一个关于太空探险的故事"}

        # Calculate full score
        start_time = time.time()
        total_score, breakdown = calculate_full_score(data, context, task_type)
        elapsed = time.time() - start_time

        print(f"\n📊 Scoring Breakdown:")
        print(f"   Technical:  {breakdown['technical']:.2f} / 20")
        print(f"   Structure:  {breakdown['structure']:.2f} / 30")
        print(f"   Content:    {breakdown['content']:.2f} / 20")
        print(f"   Narrative:  {breakdown['narrative']:.2f} / 30 (AI: {breakdown['narrative_breakdown'].get('evaluation_method', 'unknown')})")
        print(f"   ─────────────────────────")
        print(f"   TOTAL:      {total_score:.2f} / 100")
        print(f"\n   ⏱️  Scoring time: {elapsed:.2f}s")

        # Show AI notes if available
        ai_notes = breakdown['narrative_breakdown'].get('ai_notes', '')
        if ai_notes:
            print(f"   💭 AI Notes: {ai_notes[:100]}...")

        results.append({
            "task": task_type,
            "quality": quality,
            "score": total_score,
            "breakdown": breakdown
        })

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for r in results:
        status = "✅" if r["score"] > 50 else "⚠️" if r["score"] > 30 else "❌"
        print(f"   {status} {r['task']:12} ({r['quality']:7}): {r['score']:.2f}/100")

    # Validation
    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    passed = True

    # Good content should score > 50
    good_scores = [r["score"] for r in results if r["quality"] == "good"]
    poor_scores = [r["score"] for r in results if r["quality"] == "poor"]

    if good_scores and poor_scores:
        avg_good = sum(good_scores) / len(good_scores)
        avg_poor = sum(poor_scores) / len(poor_scores)

        if avg_good > avg_poor:
            print(f"✅ Good content ({avg_good:.1f}) scores higher than poor ({avg_poor:.1f})")
        else:
            print(f"❌ Good content should score higher than poor content")
            passed = False

    # All scores should be in valid range
    for r in results:
        if 0 <= r["score"] <= 100:
            print(f"✅ {r['task']} ({r['quality']}) score in valid range")
        else:
            print(f"❌ {r['task']} ({r['quality']}) score out of range: {r['score']}")
            passed = False

    if passed:
        print("\n🎉 All E2E tests passed!")
    else:
        print("\n⚠️  Some tests failed.")

    return passed


if __name__ == "__main__":
    run_e2e_test()
