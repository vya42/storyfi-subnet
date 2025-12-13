"""
Mock Story Generator - 返回预设内容，无需 API

使用方法：
1. 修改 config/generator_config.yaml:
   generator:
     mode: "mock"

2. 启动 miner，自动使用 mock 内容
"""

import json
import random
import time
from typing import Dict
from .base import StoryGenerator


# 预设的故事内容模板
MOCK_BLUEPRINTS = [
    {
        "title": "星际迷航：最后的边疆",
        "genre": "科幻",
        "setting": "2347年，人类已经殖民了银河系的三分之一",
        "core_conflict": "一艘失踪百年的殖民船突然出现，船上的冷冻舱里躺着人类始祖的克隆体",
        "themes": ["身份认同", "人性本质", "科技伦理"],
        "tone": "史诗、神秘、哲学性",
        "target_audience": "科幻爱好者，18-45岁"
    },
    {
        "title": "江湖夜雨",
        "genre": "武侠",
        "setting": "明朝末年，江湖动荡，各派势力暗流涌动",
        "core_conflict": "一本失传的武功秘籍重现江湖，引发腥风血雨",
        "themes": ["正邪之辩", "江湖情义", "权力诱惑"],
        "tone": "悲壮、浪漫、侠义",
        "target_audience": "武侠小说爱好者"
    },
    {
        "title": "硅谷风云",
        "genre": "商战",
        "setting": "2024年硅谷，AI创业公司群雄逐鹿",
        "core_conflict": "一个天才程序员发现了AGI的秘密，却被巨头公司追杀",
        "themes": ["技术理想", "资本博弈", "人性考验"],
        "tone": "紧张、烧脑、现实主义",
        "target_audience": "科技从业者，创业者"
    }
]

MOCK_CHARACTERS = [
    {
        "characters": [
            {"name": "李逍遥", "role": "主角", "personality": "正直善良，有点冲动", "background": "孤儿出身，被师傅收养"},
            {"name": "赵灵儿", "role": "女主角", "personality": "温柔聪慧，坚韧不拔", "background": "神秘身世，身负使命"},
            {"name": "林月如", "role": "女二号", "personality": "泼辣直爽，敢爱敢恨", "background": "将门之后，武艺高强"},
            {"name": "拜月教主", "role": "反派", "personality": "野心勃勃，心狠手辣", "background": "曾经的正道高手，误入歧途"},
            {"name": "酒剑仙", "role": "导师", "personality": "放荡不羁，深藏不露", "background": "隐世高人，嗜酒如命"}
        ]
    }
]

MOCK_STORY_ARCS = [
    {
        "title": "命运的交织",
        "description": "一个关于成长、友情与牺牲的史诗故事",
        "chapters": [
            {"id": 1, "title": "命运的起点", "summary": "主角的平静生活被打破"},
            {"id": 2, "title": "意外的相遇", "summary": "邂逅改变命运的人"},
            {"id": 3, "title": "第一次考验", "summary": "面对人生的第一个重大抉择"},
            {"id": 4, "title": "真相浮出", "summary": "发现隐藏的秘密"},
            {"id": 5, "title": "至暗时刻", "summary": "遭遇最大的挫折"},
            {"id": 6, "title": "绝地反击", "summary": "在绝望中找到希望"},
            {"id": 7, "title": "最终对决", "summary": "与命运的终极较量"},
            {"id": 8, "title": "新的开始", "summary": "故事的结局与新起点"}
        ],
        "arcs": ["序章", "成长篇", "试炼篇", "高潮篇"],
        "themes": ["成长", "友情", "牺牲"],
        "hooks": ["悬念设置", "情感共鸣", "反转剧情"]
    }
]

MOCK_CHAPTERS = [
    {
        "chapters": [
            {
                "id": 1,
                "title": "命运的起点",
                "content": "清晨的阳光透过窗帘的缝隙洒进房间，尘埃在光束中缓缓飘动。李逍遥从梦中惊醒，额头上渗出细密的汗珠。又是那个梦——那个他从记事起就反复出现的奇怪梦境...",
                "choices": [
                    {"text": "调查这个梦的含义", "consequence": "发现家族秘密"},
                    {"text": "当作普通的噩梦忽略", "consequence": "错过重要线索"},
                    {"text": "向师傅请教", "consequence": "获得神秘指引"}
                ]
            }
        ]
    }
]


class MockGenerator(StoryGenerator):
    """Mock generator that returns preset content without API calls."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.initialized = True
        self.init_time = time.time()
        print("🎭 Mock Generator initialized - using preset story content")

    async def generate(self, input_data: Dict) -> Dict:
        """Return mock content based on task type."""
        task_type = input_data.get('task_type', 'blueprint')

        # 模拟生成时间 (1-3秒)
        delay = random.uniform(1, 3)
        time.sleep(delay)

        # 根据任务类型返回不同的预设内容
        if task_type == 'blueprint':
            content = random.choice(MOCK_BLUEPRINTS)
        elif task_type == 'characters':
            content = random.choice(MOCK_CHARACTERS)
        elif task_type == 'story_arc':
            content = random.choice(MOCK_STORY_ARCS)
        elif task_type == 'chapters':
            content = random.choice(MOCK_CHAPTERS)
        else:
            content = {"generated_text": "Mock content for unknown task type"}

        return {
            "generated_content": json.dumps(content, ensure_ascii=False),
            "model": "mock-v1",
            "mode": "mock",
            "generation_time": delay,
            "metadata": {"mock": True, "task_type": task_type}
        }

    def get_mode(self) -> str:
        return "mock"

    def get_model_info(self) -> Dict:
        return {
            "name": "mock-generator",
            "version": "1.0.0",
            "provider": "local",
            "parameters": {"preset_count": len(MOCK_BLUEPRINTS)}
        }

    async def health_check(self) -> bool:
        return True
