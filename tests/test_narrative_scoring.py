#!/usr/bin/env python3
"""
Test script for Narrative Merit Scoring Module.

This script tests the AI-based narrative evaluation without requiring
a full Bittensor setup.

Usage:
    python tests/test_narrative_scoring.py
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoring.narrative import (
    calculate_narrative_score,
    NarrativeEvaluator,
    get_evaluator
)


def test_blueprint_scoring():
    """Test scoring a blueprint task."""
    print("\n" + "=" * 60)
    print("TEST 1: Blueprint Scoring")
    print("=" * 60)

    data = {
        "title": "星际迷途",
        "genre": "科幻冒险",
        "setting": "2150年，人类已经建立了横跨三个星系的殖民帝国。主角生活在边缘星球，那里资源匮乏但自由度高。",
        "core_conflict": "一艘神秘的外星飞船坠落在主角的星球上，带来了可能改变人类命运的技术，但也引来了帝国军队的注意。",
        "themes": ["探索未知", "自由与秩序", "人性本质"],
        "tone": "史诗感与个人冒险并重",
        "target_audience": "科幻爱好者"
    }

    context = {
        "user_input": "写一个关于太空探险的故事"
    }

    score, breakdown = calculate_narrative_score(data, context, "blueprint")

    print(f"\nScore: {score:.2f} / 30")
    print(f"\nBreakdown:")
    for key, value in breakdown.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    return score


def test_characters_scoring():
    """Test scoring a characters task."""
    print("\n" + "=" * 60)
    print("TEST 2: Characters Scoring")
    print("=" * 60)

    data = {
        "characters": [
            {
                "id": "char_001",
                "name": "林远星",
                "archetype": "不情愿的英雄",
                "background": "前帝国飞行员，因拒绝执行屠杀平民的命令而被流放到边缘星球。他失去了一切，只剩下一艘破旧的货船和对自由的渴望。",
                "motivation": "保护新家园的人们，同时找到自我救赎的道路",
                "skills": ["星际导航", "近身格斗", "机械维修"],
                "personality_traits": ["沉默寡言", "正义感强", "内心孤独"]
            },
            {
                "id": "char_002",
                "name": "艾拉",
                "archetype": "神秘向导",
                "background": "外星飞船中唯一幸存的乘客，她的种族拥有远超人类的技术，但正在走向灭亡。她是最后的希望。",
                "motivation": "寻找新的家园，同时帮助人类避免重蹈她的种族的覆辙",
                "skills": ["心灵感应", "高级科技操作", "多语言交流"],
                "personality_traits": ["温和但坚定", "智慧", "略带悲伤"]
            }
        ]
    }

    context = {
        "blueprint": {
            "title": "星际迷途",
            "genre": "科幻冒险"
        }
    }

    score, breakdown = calculate_narrative_score(data, context, "characters")

    print(f"\nScore: {score:.2f} / 30")
    print(f"\nBreakdown:")
    for key, value in breakdown.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    return score


def test_chapters_scoring():
    """Test scoring a chapters task."""
    print("\n" + "=" * 60)
    print("TEST 3: Chapters Scoring")
    print("=" * 60)

    data = {
        "chapters": [
            {
                "chapter": 1,
                "title": "坠落的星辰",
                "content": """
                夜空中划过一道炽烈的光芒，比任何流星都要明亮百倍。

                林远星放下手中的扳手，从破旧货船的引擎舱中探出头来。在这个被帝国遗忘的边缘星球上，他已经习惯了寂静的夜晚，但今晚不同。

                那道光芒没有消失，反而越来越近。他能感受到空气中弥漫的臭氧味，能听到远处传来的低沉轰鸣。

                "那不是陨石，"他自言自语，眼睛紧盯着逐渐清晰的轮廓，"那是...一艘飞船。"

                飞船坠落的地点距离他的小镇不到十公里。林远星知道，无论那是什么，帝国的探测器很快就会发现它。他有两个选择：假装什么都没看到，继续过他平静的流放生活；或者赶在帝国军队到来之前，去看看那艘飞船里到底有什么。

                他想起了五年前那个改变他一生的夜晚，想起了那些无辜的面孔，想起了自己为什么会来到这个荒凉的地方。

                "该死的，"他抓起一把激光手枪，朝着坠落点跑去，"我就不能安安静静地当个修理工吗？"
                """,
                "choices": [
                    {
                        "text": "悄悄接近飞船",
                        "consequence": "林远星选择了谨慎的方式",
                        "next_chapter": 2
                    },
                    {
                        "text": "先召集镇上的人",
                        "consequence": "林远星决定不独自冒险",
                        "next_chapter": 3
                    }
                ]
            }
        ]
    }

    context = {
        "blueprint": {
            "title": "星际迷途",
            "genre": "科幻冒险"
        }
    }

    score, breakdown = calculate_narrative_score(data, context, "chapters")

    print(f"\nScore: {score:.2f} / 30")
    print(f"\nBreakdown:")
    for key, value in breakdown.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    return score


def test_poor_quality_content():
    """Test scoring poor quality content."""
    print("\n" + "=" * 60)
    print("TEST 4: Poor Quality Content (should score low)")
    print("=" * 60)

    data = {
        "title": "故事",
        "genre": "科幻",
        "setting": "太空",
        "core_conflict": "打架",
        "themes": ["好"],
        "tone": "一般",
        "target_audience": "人"
    }

    context = {
        "user_input": "写一个关于太空探险的故事"
    }

    score, breakdown = calculate_narrative_score(data, context, "blueprint")

    print(f"\nScore: {score:.2f} / 30")
    print(f"\nBreakdown:")
    for key, value in breakdown.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    return score


def test_evaluator_stats():
    """Test evaluator statistics."""
    print("\n" + "=" * 60)
    print("TEST 5: Evaluator Statistics")
    print("=" * 60)

    evaluator = get_evaluator()
    stats = evaluator.get_stats()

    print(f"\nEvaluator Stats:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2%}" if "rate" in key else f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")

    return stats


def main():
    print("=" * 60)
    print("StoryNet Narrative Scoring Test Suite")
    print("=" * 60)

    # Check if we have a config
    config_paths = [
        os.path.expanduser("~/.storynet/narrative_config.yaml"),
        os.path.expanduser("~/.storynet/narrative_config.json"),
    ]

    config_found = False
    for path in config_paths:
        if os.path.exists(path):
            print(f"\n✅ Found config at: {path}")
            config_found = True
            break

    if not config_found:
        print("\n⚠️  No custom config found. Using default settings.")
        print("   For custom evaluation, create: ~/.storynet/narrative_config.yaml")

    # Run tests
    scores = []

    try:
        scores.append(("Blueprint", test_blueprint_scoring()))
    except Exception as e:
        print(f"\n❌ Blueprint test failed: {e}")
        scores.append(("Blueprint", None))

    try:
        scores.append(("Characters", test_characters_scoring()))
    except Exception as e:
        print(f"\n❌ Characters test failed: {e}")
        scores.append(("Characters", None))

    try:
        scores.append(("Chapters", test_chapters_scoring()))
    except Exception as e:
        print(f"\n❌ Chapters test failed: {e}")
        scores.append(("Chapters", None))

    try:
        scores.append(("Poor Quality", test_poor_quality_content()))
    except Exception as e:
        print(f"\n❌ Poor quality test failed: {e}")
        scores.append(("Poor Quality", None))

    test_evaluator_stats()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, score in scores:
        if score is not None:
            print(f"  {name}: {score:.2f} / 30")
        else:
            print(f"  {name}: FAILED")

    # Validation
    print("\n" + "=" * 60)
    print("VALIDATION")
    print("=" * 60)

    all_passed = True
    using_fallback = False

    # Check if we're using fallback (no AI available)
    evaluator = get_evaluator()
    stats = evaluator.get_stats()
    if stats["api_errors"] > 0 and stats["cache_hits"] == 0:
        using_fallback = True
        print("⚠️  AI backend not available - using fallback scores")
        print("   To test with real AI, start Ollama: ollama serve")
        print("")

    # Check that good content scores higher than poor content
    blueprint_score = scores[0][1]
    poor_score = scores[3][1]

    if not using_fallback:
        if blueprint_score is not None and poor_score is not None:
            if blueprint_score > poor_score:
                print("✅ Good content scores higher than poor content")
            else:
                print("❌ Good content should score higher than poor content")
                all_passed = False
    else:
        print("⏭️  Skipping quality comparison (fallback mode)")

    # Check that scores are in valid range
    for name, score in scores:
        if score is not None:
            if 0 <= score <= 30:
                print(f"✅ {name} score in valid range (0-30)")
            else:
                print(f"❌ {name} score out of range: {score}")
                all_passed = False

    if all_passed:
        print("\n🎉 All tests passed!")
        if using_fallback:
            print("   (Note: Run with AI backend for full testing)")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
