# ============================================================
# 自媒体 Skill 每周雷达 pipeline (GHA / 本地双模)
# 源: https://github.com/UnderleveledBuilder/awesome-social-media-skills (catalog.json)
# 每周: 拉取最新 catalog → 与 state.json 做差集(持续发现新技能)
#       → 筛选有价值技能 + 星级排列 → 生成排版 HTML 周报 → SMTP 发邮件 → 归档
#
# 凭据解析顺序:
#   环境变量 SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/EMAIL_FROM/EMAIL_TO
#   → 本地回退: 1727027266@qq.com + D:\Hermes\job_push\secrets\email_pass.txt
# 开关:
#   NO_EMAIL=1  只生成文档不发送(本地试运行)
#   STATE_FILE  状态文件路径(默认: 本文件同目录 state.json)
#   OUTPUT_DIR  归档目录(默认: 本文件同目录 reports/)
#
# 运行: python pipeline.py   (GHA: ubuntu; 本地: Windows)
# ============================================================

import json
import os
import re
import sys
import smtplib
import urllib.request
import logging
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders as _enc
from email.header import Header
from email.utils import formataddr

BASE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.environ.get("STATE_FILE", os.path.join(BASE, "state.json"))
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(BASE, "reports"))
LOCAL_SMTP_SECRET = r"D:\Hermes\job_push\secrets\email_pass.txt"  # 本地回退(QQ 授权码)

CATALOG_URL = "https://raw.githubusercontent.com/UnderleveledBuilder/awesome-social-media-skills/main/catalog.json"
SOURCE_REPO = "https://github.com/UnderleveledBuilder/awesome-social-media-skills"
DEFAULT_SMTP = {"host": "smtp.qq.com", "port": 465}
DEFAULT_FROM = "1727027266@qq.com"
DEFAULT_TO = "385096659@qq.com"
SENDER_NAME = "自媒体Skill雷达"

# 用户核心平台(运营画像: 小红书日更、抖音/视频号、公众号、YouTube)
CORE_PLATFORMS = {"xiaohongshu", "douyin", "wechat", "channels", "youtube"}

# 星级阈值: (最少 stars, 星数, 基础分)
TIER_RULES = [
    (2500, 5, 100),
    (500, 4, 80),
    (100, 3, 60),
    (20, 2, 40),
    (0, 1, 20),
]
FEATURED_BONUS = 15
SKILL_FORMAT_BONUS = 5
CORE_PLATFORM_BONUS = 10
ACTIVE_BONUS = 5  # 30 天内有 push
TOP_N = 15

os.makedirs(OUTPUT_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler(os.path.join(OUTPUT_DIR, "pipeline.log"), encoding="utf-8")],
)
log = logging.getLogger("social-skills-radar")


def get_smtp_credentials():
    host, port = os.environ.get("SMTP_HOST", ""), os.environ.get("SMTP_PORT", "")
    user, pw = os.environ.get("SMTP_USER", ""), os.environ.get("SMTP_PASSWORD", "")
    to = os.environ.get("EMAIL_TO", DEFAULT_TO)
    if host and user and pw:
        return {"host": host, "port": int(port or "465"), "user": user, "pw": pw, "to": to}
    if not os.path.exists(LOCAL_SMTP_SECRET):
        raise RuntimeError("缺少 SMTP 凭据: GHA 需设 secrets, 本地需有 " + LOCAL_SMTP_SECRET)
    with open(LOCAL_SMTP_SECRET, "r", encoding="utf-8") as f:
        pw = f.read().strip()
    if not pw:
        raise RuntimeError("本地邮件授权码为空")
    return {"host": DEFAULT_SMTP["host"], "port": DEFAULT_SMTP["port"], "user": DEFAULT_FROM, "pw": pw, "to": to}


# -----------------------------------------------------------
# 数据获取
# -----------------------------------------------------------
def fetch_catalog():
    if os.environ.get("CATALOG_FILE"):
        with open(os.environ["CATALOG_FILE"], "r", encoding="utf-8") as f:
            catalog = json.load(f)
        log.info("catalog 从本地文件加载: %s entries=%d", os.environ["CATALOG_FILE"], len(catalog.get("entries", [])))
        return catalog
    last_error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(CATALOG_URL, headers={"User-Agent": "social-skills-radar/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                catalog = json.loads(resp.read().decode("utf-8"))
            log.info("catalog 拉取成功: updated=%s entries=%d", catalog.get("updated"), len(catalog.get("entries", [])))
            return catalog
        except Exception as e:
            last_error = e
            log.warning("拉取失败(第%d次): %s", attempt + 1, e)
    cache = os.path.join(BASE, "catalog.cache.json")
    if os.path.exists(cache):
        log.warning("使用本地缓存 catalog (原因: %s)", last_error)
        with open(cache, "r", encoding="utf-8") as f:
            return json.load(f)
    raise RuntimeError(f"catalog 拉取失败且无缓存: {last_error}")


# -----------------------------------------------------------
# 评分与筛选
# -----------------------------------------------------------
def star_tier(stars, featured=False):
    """返回 (星数, 基础分)。精选项目允许从次档晋升 5 星。"""
    for i, (threshold, n, pts) in enumerate(TIER_RULES):
        if stars >= threshold:
            return n, pts
        if featured and i == 0 and stars >= TIER_RULES[1][0]:
            return 5, 100
    return 1, TIER_RULES[-1][2]


def pushed_recently(entry, within_days=30):
    p = entry.get("pushed_at") or ""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", p)
    if not m:
        return False
    try:
        d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return (date.today() - d).days <= within_days
    except ValueError:
        return False


def score_entry(entry):
    stars = entry.get("stars", 0) or 0
    featured = bool(entry.get("featured"))
    tier, score = star_tier(stars, featured)
    if featured:
        score += FEATURED_BONUS
    if entry.get("format") == "skill":
        score += SKILL_FORMAT_BONUS
    if CORE_PLATFORMS & set(entry.get("platforms", [])):
        score += CORE_PLATFORM_BONUS
    if pushed_recently(entry):
        score += ACTIVE_BONUS
    return tier, score


def fmt_stars(n):
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def compute_week(catalog, state):
    entries = catalog["entries"]
    seen = state.get("seen", {})
    first_run = not seen

    new_entries, star_movers = [], []
    for e in entries:
        repo = e["repo"]
        stars = e.get("stars", 0) or 0
        tier, score = score_entry(e)
        item = dict(e)
        item["_tier"], item["_score"] = tier, score
        prev = seen.get(repo)
        if not first_run:
            if prev is None:
                new_entries.append(item)
            else:
                prev_stars = prev.get("stars_last", 0) or 0
                if stars - prev_stars >= 50 and stars >= prev_stars * 1.15:
                    item["_delta"] = stars - prev_stars
                    star_movers.append(item)
    ranked = sorted(
        entries,
        key=lambda x: (-score_entry(x)[1], -(x.get("stars", 0) or 0), x["name"].lower()),
    )
    top = []
    for e in ranked[:TOP_N]:
        tier, score = score_entry(e)
        item = dict(e)
        item["_tier"], item["_score"] = tier, score
        top.append(item)
    new_entries.sort(key=lambda x: (-x["_tier"], -(x.get("stars", 0) or 0)))
    star_movers.sort(key=lambda x: -x.get("_delta", 0))
    return first_run, new_entries, star_movers, top


# -----------------------------------------------------------
# 文档生成
# -----------------------------------------------------------
GROUP_CN = {
    "pipeline": "全流程运营",
    "writing": "文案创作",
    "visual": "排版/封面/短视频",
    "publish": "发布自动化",
    "research": "选题/热点/数据",
    "strategy": "账号定位增长",
    "mcp": "MCP/命令行",
    "apps": "开源平台",
}
PLATFORM_CN = {
    "xiaohongshu": "小红书", "douyin": "抖音", "wechat": "公众号",
    "channels": "视频号", "bilibili": "B站", "youtube": "YouTube",
    "tiktok": "TikTok", "x": "X", "instagram": "Ins", "linkedin": "LinkedIn",
    "zhihu": "知乎", "toutiao": "头条", "weibo": "微博", "kuaishou": "快手",
    "facebook": "FB", "reddit": "Reddit", "pinterest": "Pinterest",
    "threads": "Threads", "substack": "Substack", "general": "通用",
}


def stars_html(tier, stars):
    color = {5: "#d4a017", 4: "#d4a017", 3: "#c98a2c", 2: "#b5b5b5", 1: "#b5b5b5"}[tier]
    return (f'<span style="color:{color};letter-spacing:1px;">{"★" * tier}</span> '
            f'<span style="color:#bbb;">{"☆" * (5 - tier)}</span> <b>{fmt_stars(stars)}</b>')


def plat_list(entry):
    plats = [str(PLATFORM_CN.get(p, p)) for p in (entry.get("platforms") or [])[:4]]
    total = len(entry.get("platforms") or [])
    return "、".join(plats) + (f" 等{total}个" if total > 4 else "")


def entry_row(rank, item):
    name = item["name"]
    url = item["url"]
    desc = (item.get("desc") or "").strip()
    if len(desc) > 72:
        desc = desc[:72] + "…"
    install = item.get("install") or ""
    install_cell = (f'<code style="background:#f0f1f5;padding:2px 6px;border-radius:4px;'
                    f'font-size:12px;white-space:nowrap;">{install}</code>') if install else "-"
    badge = (' <span style="background:#d4a017;color:#fff;font-size:11px;padding:1px 6px;'
             'border-radius:8px;">精选</span>') if item.get("featured") else ""
    return f"""<tr>
<td style="text-align:center;color:#999;font-weight:bold;">{rank}</td>
<td style="white-space:nowrap;">{stars_html(item["_tier"], item.get("stars", 0) or 0)}</td>
<td><a href="{url}" style="color:#1a6ef5;text-decoration:none;font-weight:bold;">{name}</a>{badge}<br>
<span style="color:#666;font-size:13px;">{desc}</span><br>
<span style="color:#999;font-size:12px;">{GROUP_CN.get(item.get("group",""), item.get("group",""))} · {plat_list(item)}</span><br>
{install_cell}</td></tr>"""


def build_html(catalog, first_run, new_entries, star_movers, top, today):
    total = len(catalog.get("entries", []))
    feat = sum(1 for e in catalog["entries"] if e.get("featured"))
    week_no = today.isocalendar().week

    if new_entries:
        rows = "".join(entry_row(i + 1, e) for i, e in enumerate(new_entries[:30]))
        new_section = (f'<h2>🆕 本周新发现 <span style="color:#888;font-size:14px;">({len(new_entries)})</span></h2>'
                       f'<table style="border-collapse:collapse;width:100%;font-size:14px;">'
                       f'<tr><th></th><th style="width:150px;text-align:center;"></th><th></th></tr>{rows}</table>')
    elif first_run:
        new_section = (f'<h2>🆕 本周新发现</h2><p style="color:#888;">'
                       f'本期为基线期: 全部 {total} 个项目已登记, 从下期起报告新增。</p>')
    else:
        new_section = '<h2>🆕 本周新发现</h2><p style="color:#888;">本周无新收录。</p>'

    mover_section = ""
    if star_movers:
        lines = []
        for e in star_movers[:10]:
            lines.append(
                f'<li><a href="{e["url"]}" style="color:#1a6ef5;">{e["name"]}</a> '
                f'★ {fmt_stars(e.get("stars",0))} <span style="color:#2e9e5b;">(+{e.get("_delta",0)})</span>'
                f'<span style="color:#999;font-size:13px;"> · {GROUP_CN.get(e.get("group",""))}</span></li>')
        mover_section = '<h2>📈 星标大涨</h2><ul style="font-size:14px;">' + "".join(lines) + "</ul>"

    top_rows = "".join(entry_row(i + 1, e) for i, e in enumerate(top))
    top_section = (f'<h2>🏆 有价值排行 TOP {len(top)} <span style="color:#888;font-size:14px;">(按价值分 × 星级排列)</span></h2>'
                   f'<table style="border-collapse:collapse;width:100%;font-size:14px;">'
                   f'<tr><th></th><th style="width:150px;text-align:center;"></th><th></th></tr>{top_rows}</table>')

    return f"""<html><body style="margin:0;padding:20px;background:#f5f6f8;font-family:'Microsoft YaHei','PingFang SC',sans-serif;">
<div style="max-width:760px;margin:0 auto;background:#ffffff;border-radius:10px;padding:28px 32px;color:#222;line-height:1.7;">
<h1 style="font-size:22px;border-bottom:3px solid #d4a017;padding-bottom:12px;">自媒体 Skill 周报 <span style="font-size:14px;color:#999;">第 {week_no} 周 · {today.isoformat()}</span></h1>
<p style="font-size:13px;color:#888;">来源: <a href="{SOURCE_REPO}" style="color:#1a6ef5;">awesome-social-media-skills</a>
· 收录 {total} 个 (精选 {feat}) · 目录更新于 {catalog.get("updated","?")} · 价值分 = 星级基础分 + 精选 + 技能格式 + 平台契合 + 活跃</p>
{new_section}
{mover_section}
{top_section}
<h2>🧭 使用提示</h2>
<ul style="font-size:13px;color:#666;">
<li>安装: 支持 skills 协议的 agent 直接 <code>npx skills add &lt;owner/repo&gt;</code>; 其余 agent 把 SKILL.md 放进 skills 目录。</li>
<li>安全: 能代发帖的技能会存你的登录 cookie, 装前读一遍它的 SKILL.md; 平台对批量自动化有限流/封号风险。</li>
<li>每周自动推送 (GitHub Actions), 数据源 <a href="{SOURCE_REPO}" style="color:#1a6ef5;">catalog.json</a>。</li>
</ul>
<p style="color:#bbb;font-size:12px;border-top:1px solid #eee;padding-top:12px;">
由每周雷达自动生成 · {datetime.now().strftime("%Y-%m-%d %H:%M")} · 数据源持续更新, 排名可能小幅变动</p>
</div></body></html>"""


def build_md(catalog, first_run, new_entries, star_movers, top, today):
    lines = [
        f"# 自媒体 Skill 周报 · 第 {today.isocalendar().week} 周 ({today.isoformat()})",
        "",
        f"- 来源: {SOURCE_REPO} (收录 {len(catalog['entries'])} 个, 目录更新于 {catalog.get('updated')})",
        "",
    ]
    if new_entries:
        lines += [f"## 🆕 本周新发现 ({len(new_entries)})", ""]
        for i, e in enumerate(new_entries, 1):
            lines.append(
                f"{i}. {'★' * e['_tier']} [{e['name']}]({e['url']}) ★{fmt_stars(e.get('stars',0))} · "
                f"{GROUP_CN.get(e.get('group',''))} · {(e.get('desc') or '')[:60]}")
    else:
        lines += ["## 🆕 本周新发现", ""]
        lines.append("基线期, 无新增报告。" if first_run else "本周无新收录。")
    if star_movers:
        lines += ["", "## 📈 星标大涨", ""]
        for e in star_movers:
            lines.append(f"- {e['name']} ★{fmt_stars(e.get('stars',0))} (+{e.get('_delta',0)})")
    lines += ["", f"## 🏆 有价值排行 TOP {len(top)}", ""]
    for i, e in enumerate(top, 1):
        lines.append(
            f"{i}. {'★' * e['_tier']} [{e['name']}]({e['url']}) ★{fmt_stars(e.get('stars',0))} · 价值分{e['_score']} · "
            f"{GROUP_CN.get(e.get('group',''))} · {(e.get('desc') or '')[:50]}")
    return "\n".join(lines)


# -----------------------------------------------------------
# 邮件发送
# -----------------------------------------------------------
def send_email(subject, html, md_path, creds):
    if os.environ.get("NO_EMAIL") == "1":
        log.info("NO_EMAIL=1, 跳过发送")
        return True
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((SENDER_NAME, creds["user"]))
    msg["To"] = creds["to"]
    msg["Subject"] = Header(subject, "utf-8")
    msg.attach(MIMEText(html, "html", "utf-8"))
    if md_path and os.path.exists(md_path):
        part = MIMEBase("application", "octet-stream")
        with open(md_path, "rb") as f:
            part.set_payload(f.read())
        _enc.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=("utf-8", "", "weekly_report.md"))
        msg.attach(part)

    with smtplib.SMTP_SSL(creds["host"], creds["port"], timeout=30) as server:
        server.login(creds["user"], creds["pw"])
        server.sendmail(creds["user"], [creds["to"]], msg.as_string())
    log.info("邮件发送成功 → %s (via %s)", creds["to"], creds["host"])
    return True


# -----------------------------------------------------------
# state
# -----------------------------------------------------------
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(catalog, today, run_count):
    entries = catalog.get("entries", [])
    state = {
        "seen": {
            e["repo"]: {
                "stars_last": e.get("stars", 0) or 0,
                "pushed_last": e.get("pushed_at", ""),
                "catalog_updated": catalog.get("updated", ""),
            }
            for e in entries
        },
        "last_run": today.isoformat(),
        "catalog_updated": catalog.get("updated", ""),
        "run_count": run_count,
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    log.info("state 已更新: %d 个 repo 登记 → %s", len(state["seen"]), STATE_FILE)


# -----------------------------------------------------------
# 主流程
# -----------------------------------------------------------
def main():
    today = date.today()
    catalog = fetch_catalog()
    state = load_state()
    run_count = int(state.get("run_count", 0)) + 1
    first_run, new_entries, star_movers, top = compute_week(catalog, state)

    html = build_html(catalog, first_run, new_entries, star_movers, top, today)
    md = build_md(catalog, first_run, new_entries, star_movers, top, today)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    week = today.isocalendar().week
    md_path = os.path.join(OUTPUT_DIR, f"weekly_report_{today.isoformat()}_w{week}.md")
    html_path = os.path.join(OUTPUT_DIR, f"weekly_report_{today.isoformat()}_w{week}.html")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    log.info("文档已生成: %s / %s", md_path, html_path)

    creds = get_smtp_credentials()
    subject = f"【自媒体Skill周报】第{week}周 · 新发现{len(new_entries)} · 有价值TOP{len(top)}"
    ok = send_email(subject, html, md_path, creds)
    if not ok:
        raise RuntimeError("邮件发送失败")
    save_state(catalog, today, run_count)

    print(
        f"OK week={week} new={len(new_entries)} movers={len(star_movers)} top={len(top)} "
        f"total={len(catalog['entries'])} catalog_updated={catalog.get('updated')} "
        f"email_to={creds['to']} md={md_path}"
    )


if __name__ == "__main__":
    main()
