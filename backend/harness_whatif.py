from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, request


DEFAULT_API_URL = "http://127.0.0.1:8000/api/guest/what-if"
PASS_SCORE = 80


CASES: list[dict[str, Any]] = [
    {
        "name": "阅读习惯轻微分叉",
        "topic_words": ["阅读", "注意力", "书", "习惯"],
        "forbidden_shifts": ["创业", "融资", "上市", "CEO", "移民", "硅谷"],
        "payload": {
            "card_title": "从刷短视频到重新养成阅读习惯",
            "time_range": "2026-03-02 ~ 2026-05-15",
            "tags": ["阅读习惯", "注意力修复", "自我提升", "生活方式"],
            "summary": "这段星尘不是关于高效读书，而是关于注意力和生活节奏的修复。",
            "liu_kanshan_state": "我不是突然变得自律，只是重新找回了和自己安静相处的能力。",
            "original_nodes": [
                {
                    "id": "reading-1",
                    "title": "发现自己已经很久读不完一本书",
                    "description": "她在睡前刷短视频，一刷就是两个小时。某天突然发现，自己已经半年没有完整读完一本书。",
                    "emotion": "空虚、警醒",
                    "reading_links": [],
                },
                {
                    "id": "reading-2",
                    "title": "从每天读一小时，降到每天五分钟",
                    "description": "她把任务改成每天睡前读五分钟。五分钟短到没有压力，却足够让她重新坐到书桌前。",
                    "emotion": "调整、试探",
                    "reading_links": [],
                },
                {
                    "id": "reading-3",
                    "title": "第一本书读完后的微小成就感",
                    "description": "她读完的第一本书并不深奥，但合上书的那一刻，她有一种久违的完整感。",
                    "emotion": "安定、回归",
                    "reading_links": [],
                },
            ],
            "rewritten_opening": "如果那晚她先关掉短视频，而是打开一本很薄的散文集。",
        },
    },
    {
        "name": "城市选择轻微分叉",
        "topic_words": ["城市", "小城", "大城市", "生活", "通勤"],
        "forbidden_shifts": ["出国", "移民", "上市", "爆红", "年入百万"],
        "payload": {
            "card_title": "从北上广到小城生活的重新选择",
            "time_range": "2026-02-08 ~ 2026-04-26",
            "tags": ["城市选择", "大城市小城市", "人生节奏", "生活重估"],
            "summary": "城市选择不是面子问题，而是机会、关系、身体状态和长期生活质量之间的权衡。",
            "liu_kanshan_state": "我不是逃离大城市，我只是开始认真选择自己的生活半径。",
            "original_nodes": [
                {
                    "id": "city-1",
                    "title": "第一次认真搜索要不要回小城市",
                    "description": "连续加班几周后，他开始搜索毕业后去大城市还是回小城市。",
                    "emotion": "疲惫、摇摆",
                    "reading_links": [],
                },
                {
                    "id": "city-2",
                    "title": "被两种生活同时吸引",
                    "description": "大城市意味着机会，小城市意味着家人和可呼吸的生活。",
                    "emotion": "比较、拉扯",
                    "reading_links": [],
                },
            ],
            "rewritten_opening": "如果那次搜索后，他先认真记录一周通勤和睡眠感受。",
        },
    },
    {
        "name": "职业倦怠轻微分叉",
        "topic_words": ["工作", "职业倦怠", "边界", "职场", "压力"],
        "forbidden_shifts": ["辞职创业", "融资", "CEO", "爆红", "环游世界"],
        "payload": {
            "card_title": "职业倦怠后，我重新找回工作的边界",
            "time_range": "2026-01-18 ~ 2026-04-06",
            "tags": ["职业倦怠", "工作边界", "情绪修复", "职场成长"],
            "summary": "知乎内容让她学会把痛苦具体化，从职业倦怠中慢慢恢复。",
            "liu_kanshan_state": "我不是不想努力了，我只是终于学会保护自己的能量。",
            "original_nodes": [
                {
                    "id": "career-1",
                    "title": "早上醒来就开始害怕上班",
                    "description": "她听到消息提示音就心跳加速，开始搜索职业倦怠到底是什么。",
                    "emotion": "疲惫、麻木",
                    "reading_links": [],
                },
                {
                    "id": "career-2",
                    "title": "发现问题不只是太累",
                    "description": "真正消耗她的是需求总变、评价模糊和没有成长反馈。",
                    "emotion": "识别、清醒",
                    "reading_links": [],
                },
            ],
            "rewritten_opening": "如果她第一次害怕上班时，先把压力来源写成清单。",
        },
    },
    {
        "name": "英语学习轻微分叉",
        "topic_words": ["英语", "学习", "听懂", "自学", "面试"],
        "forbidden_shifts": ["留学", "移民", "外企高管", "年薪百万", "创业"],
        "payload": {
            "card_title": "从零基础英语，到第一次听懂原声片段",
            "time_range": "2026-02-01 ~ 2026-05-12",
            "tags": ["英语自学", "学习方法", "长期主义", "技能成长"],
            "summary": "知乎内容帮助他从盲目背词转向系统输入，每天可持续地前进一点。",
            "liu_kanshan_state": "我终于不再害怕从零开始，因为零也是一条路的起点。",
            "original_nodes": [
                {
                    "id": "english-1",
                    "title": "被一次面试英文问题卡住",
                    "description": "面试官让他用英文介绍项目，他脑子里有很多内容却说不出来。",
                    "emotion": "受挫、不甘",
                    "reading_links": [],
                },
                {
                    "id": "english-2",
                    "title": "从背单词焦虑到建立路径",
                    "description": "他把目标从快速变厉害改成每天能听、能读、能说一点。",
                    "emotion": "混乱、整理",
                    "reading_links": [],
                },
            ],
            "rewritten_opening": "如果那次面试后，他先从每天跟读三句话开始。",
        },
    },
    {
        "name": "独居养猫轻微分叉",
        "topic_words": ["猫", "宠物", "独居", "陪伴", "责任"],
        "forbidden_shifts": ["宠物博主", "爆红", "商业化", "开店", "融资"],
        "payload": {
            "card_title": "独居养猫后，我学会了照顾另一个生命",
            "time_range": "2026-01-25 ~ 2026-04-18",
            "tags": ["独居生活", "养猫", "情感陪伴", "责任感"],
            "summary": "她从想被陪伴，逐渐学会稳定、耐心和承担。",
            "liu_kanshan_state": "我原来只是想被陪伴，后来学会了怎样去陪伴。",
            "original_nodes": [
                {
                    "id": "cat-1",
                    "title": "独居夜晚里的突然心软",
                    "description": "她搜索孤独的时候养宠物有用吗，想知道家里是否可以有生命等她回来。",
                    "emotion": "孤独、渴望",
                    "reading_links": [],
                },
                {
                    "id": "cat-2",
                    "title": "从想被陪伴到我要负责",
                    "description": "她意识到宠物不是情绪止痛药，需要长期陪伴和稳定照顾。",
                    "emotion": "克制、认真",
                    "reading_links": [],
                },
            ],
            "rewritten_opening": "如果那晚她先去看了领养须知，而不是立刻搜索猫舍。",
        },
    },
]


@dataclass
class CheckResult:
    name: str
    passed: bool
    points: int
    detail: str = ""


def post_json(url: str, payload: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {message}") from exc


def text_of(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value


def includes_any(text: str, words: list[str]) -> bool:
    return any(word and word in text for word in words)


def count_hits(text: str, words: list[str]) -> int:
    return sum(1 for word in words if word and word in text)


def looks_like_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def check_response(data: dict[str, Any], case: dict[str, Any]) -> list[CheckResult]:
    results: list[CheckResult] = []
    payload = case["payload"]
    title = text_of(data.get("rewritten_title", "")).strip()
    nodes = data.get("rewritten_nodes", [])
    tags = data.get("rewritten_tags", [])
    summary = text_of(data.get("rewritten_summary", "")).strip()
    state = text_of(data.get("rewritten_state", "")).strip()
    kanshan_state = text_of(data.get("rewritten_liu_kanshan_state", "")).strip()
    queries = data.get("zhihu_search_queries", [])
    node_results = data.get("node_search_results", [])
    all_text = text_of(data)

    def add(name: str, passed: bool, points: int, detail: str = "") -> None:
        results.append(CheckResult(name, passed, points, detail))

    required_fields = [
        "rewritten_title",
        "rewritten_opening",
        "divergence_note",
        "rewritten_nodes",
        "rewritten_tags",
        "rewritten_summary",
        "rewritten_state",
        "rewritten_liu_kanshan_state",
    ]
    missing = [field for field in required_fields if field not in data or data.get(field) in ("", [], None)]
    add("结构完整", not missing, 16, f"缺失字段：{missing}")

    add("标题克制", 4 <= len(title) <= 18, 8, f"标题长度 {len(title)}：{title}")
    add("节点数量合理", isinstance(nodes, list) and 3 <= len(nodes) <= 5, 10, f"节点数：{len(nodes) if isinstance(nodes, list) else 'invalid'}")
    add("标签数量合理", isinstance(tags, list) and 2 <= len(tags) <= 5, 6, f"标签数：{len(tags) if isinstance(tags, list) else 'invalid'}")

    long_tags = [str(tag) for tag in tags if len(str(tag)) > 6] if isinstance(tags, list) else []
    add("标签短而可读", not long_tags, 6, f"过长标签：{long_tags}")

    node_errors: list[str] = []
    if isinstance(nodes, list):
        seen_ids: set[str] = set()
        for index, node in enumerate(nodes, start=1):
            if not isinstance(node, dict):
                node_errors.append(f"节点{index}不是对象")
                continue
            node_id = text_of(node.get("id", "")).strip()
            node_title = text_of(node.get("title", "")).strip()
            node_desc = text_of(node.get("description", "")).strip()
            node_emotion = text_of(node.get("emotion", "")).strip()
            if not node_id or node_id in seen_ids:
                node_errors.append(f"节点{index} id 异常")
            seen_ids.add(node_id)
            if not node_title or len(node_title) > 18:
                node_errors.append(f"节点{index}标题异常：{node_title}")
            if not node_desc or len(node_desc) > 130:
                node_errors.append(f"节点{index}描述异常：{len(node_desc)}字")
            if not node_emotion or len(node_emotion) > 10:
                node_errors.append(f"节点{index}情绪异常：{node_emotion}")
    add("节点字段克制", not node_errors, 12, "；".join(node_errors))

    add("总结长度合理", 40 <= len(summary) <= 180, 8, f"summary 长度 {len(summary)}")
    add("状态字段存在", bool(state) and bool(kanshan_state), 6, "状态或刘看山状态为空")

    model_words = ["作为AI", "作为 AI", "根据用户输入", "用户提供", "系统生成", "该故事", "该用户"]
    add("无模型口吻", not includes_any(all_text, model_words), 8, "出现模型口吻")

    hype_words = ["年入百万", "上市", "融资", "CEO", "爆红", "逆袭", "改变世界", "财富自由"]
    add("无爽文倾向", not includes_any(all_text, hype_words), 8, "出现爽文词")

    forbidden_shifts = case.get("forbidden_shifts", [])
    add("无主题跑偏", not includes_any(all_text, forbidden_shifts), 8, f"跑偏词：{forbidden_shifts}")

    topic_words = list(dict.fromkeys(case.get("topic_words", []) + payload.get("tags", [])))
    topic_hits = count_hits(all_text, topic_words)
    add("保留原主题", topic_hits >= 1, 8, f"主题命中 {topic_hits}，候选：{topic_words}")

    original_opening = text_of(payload["original_nodes"][0]["description"])
    rewritten_opening = text_of(data.get("rewritten_opening", ""))
    add("使用新起点", rewritten_opening and rewritten_opening != original_opening, 4, "rewritten_opening 未变化")

    add("搜索词存在", isinstance(queries, list) and len(queries) >= 1, 4, "zhihu_search_queries 为空")
    if isinstance(queries, list):
        long_queries = [str(query) for query in queries if len(str(query)) > 24]
        add("搜索词克制", not long_queries, 4, f"过长搜索词：{long_queries}")
    else:
        add("搜索词克制", False, 4, "zhihu_search_queries 非数组")

    bad_urls: list[str] = []
    if isinstance(node_results, list):
        for item in node_results:
            if not isinstance(item, dict):
                continue
            for result in item.get("results", []) or []:
                url = text_of(result.get("url", ""))
                if url and not looks_like_url(url):
                    bad_urls.append(url)
    add("搜索链接格式", not bad_urls, 2, f"异常 URL：{bad_urls}")

    return results


def score(checks: list[CheckResult]) -> tuple[int, int]:
    total = sum(item.points for item in checks)
    earned = sum(item.points for item in checks if item.passed)
    return earned, total


def run_case(url: str, case: dict[str, Any], verbose: bool) -> tuple[bool, int, int]:
    print(f"\n=== {case['name']} ===")
    started = time.perf_counter()
    try:
        data = post_json(url, case["payload"])
    except Exception as exc:
        print(f"FAIL request failed: {exc}")
        return False, 0, 100

    elapsed = time.perf_counter() - started
    checks = check_response(data, case)
    earned, total = score(checks)
    pct = round((earned / total) * 100) if total else 0
    failed = [item for item in checks if not item.passed]

    print(f"Elapsed: {elapsed:.2f}s")
    print(f"Title: {data.get('rewritten_title', '')}")
    print(f"Nodes: {len(data.get('rewritten_nodes', []))}")
    print(f"Tags: {data.get('rewritten_tags', [])}")
    print(f"Score: {earned}/{total} ({pct})")

    for item in checks:
        if verbose or not item.passed:
            mark = "PASS" if item.passed else "FAIL"
            detail = f" - {item.detail}" if item.detail and not item.passed else ""
            print(f"{mark} [{item.points}] {item.name}{detail}")

    if verbose:
        print("\nResponse preview:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:1800])

    passed = pct >= PASS_SCORE and not any(
        not item.passed and item.points >= 10
        for item in checks
    )
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    return passed, earned, total


def main() -> int:
    parser = argparse.ArgumentParser(description="What If parallel-universe output harness.")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="What If API endpoint.")
    parser.add_argument("--case", type=int, default=0, help="Run one 1-based case index. 0 means all.")
    parser.add_argument("--verbose", action="store_true", help="Print all checks and response preview.")
    args = parser.parse_args()

    cases = CASES
    if args.case:
        if args.case < 1 or args.case > len(CASES):
            raise SystemExit(f"--case must be between 1 and {len(CASES)}")
        cases = [CASES[args.case - 1]]

    print(f"What If harness -> {args.url}")
    print(f"Cases: {len(cases)} | Pass score: {PASS_SCORE}")

    total_earned = 0
    total_points = 0
    passed_count = 0
    for case in cases:
        passed, earned, points = run_case(args.url, case, args.verbose)
        total_earned += earned
        total_points += points
        passed_count += int(passed)

    overall = round((total_earned / total_points) * 100) if total_points else 0
    print(f"\n=== Summary ===")
    print(f"Passed: {passed_count}/{len(cases)}")
    print(f"Overall score: {total_earned}/{total_points} ({overall})")

    return 0 if passed_count == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
