from pathlib import Path
import random
from collections import defaultdict

import pandas as pd
import streamlit as st
from streamlit_local_storage import LocalStorage

from db import init_db, save_submission, get_community_leaderboard, clear_all_votes


st.set_page_config(page_title="Sephiria 武器投票", layout="wide")

TOTAL_VOTES = 50
MAX_APPEARANCES_PER_WEAPON = 5
IMAGE_DIR = Path("weapon_images")
LOCAL_VOTED_KEY = "sephiria_voted"

local_storage = LocalStorage()

weapons = [
    {"id": 1001, "name": "星光闪烁"},
    {"id": 1002, "name": "冰冷愤怒"},
    {"id": 1003, "name": "岩石剑"},
    {"id": 1004, "name": "灰烬飘扬"},
    {"id": 1005, "name": "无垠原野"},
    {"id": 1006, "name": "收紧的恐惧"},
    {"id": 1007, "name": "胡萝卜剑"},
    {"id": 1008, "name": "葱根剑"},
    {"id": 1009, "name": "闪光的细剑"},
    {"id": 1010, "name": "火焰凝视"},
    {"id": 1011, "name": "冰之呼吸"},
    {"id": 1012, "name": "雷电之翼的振动"},
    {"id": 1013, "name": "冰川之刃"},
    {"id": 1014, "name": "暴风雪的前奏"},
    {"id": 1015, "name": "弩炮剑"},
    {"id": 1016, "name": "超导体"},
    {"id": 2001, "name": "默杀"},
    {"id": 2002, "name": "爱的眼神"},
    {"id": 2003, "name": "短暂自责"},
    {"id": 2004, "name": "红蛇碎击"},
    {"id": 2005, "name": "索利斯灰烬"},
    {"id": 2006, "name": "荆棘棒"},
    {"id": 2007, "name": "顽皮的恶作剧"},
    {"id": 2008, "name": "吱嘎的脊椎"},
    {"id": 2009, "name": "万年寒霜巨剑"},
    {"id": 2010, "name": "冰柱剑"},
    {"id": 2011, "name": "驱魔的重剑"},
    {"id": 2012, "name": "深红漩涡"},
    {"id": 2013, "name": "裁判官"},
    {"id": 2014, "name": "电击大剑E3G"},
    {"id": 2015, "name": "电击大剑S3G"},
    {"id": 2016, "name": "幻术师的遗产"},
    {"id": 2017, "name": "太初形态"},
    {"id": 2018, "name": "拉扎里恩"},
    {"id": 3001, "name": "无光之刃"},
    {"id": 3002, "name": "绝对向往"},
    {"id": 3003, "name": "爬行的绝望"},
    {"id": 3004, "name": "艰难实验"},
    {"id": 3005, "name": "炙热之刃"},
    {"id": 3006, "name": "燃烧之牙"},
    {"id": 3007, "name": "笼罩的阴云"},
    {"id": 3008, "name": "雷电之怒"},
    {"id": 3009, "name": "福寿草"},
    {"id": 3010, "name": "黑幕"},
    {"id": 3011, "name": "无尽沉浸"},
    {"id": 3012, "name": "模仿之书"},
    {"id": 3013, "name": "学院魔法剑：解放"},
    {"id": 4001, "name": "重型弩：加速核心"},
    {"id": 4002, "name": "弩：双子"},
    {"id": 4003, "name": "重型弩：火药合成"},
    {"id": 4004, "name": "重型弩：爆炸装置"},
    {"id": 4005, "name": "重型弩：连发装置"},
    {"id": 4006, "name": "重型弩：配备制导模块"},
    {"id": 4007, "name": "迷你加农炮"},
    {"id": 4008, "name": "重型弩：标记稳定化"},
    {"id": 4009, "name": "重型弩：聚云者"},
    {"id": 4010, "name": "重型弩：速冻结晶"},
    {"id": 4011, "name": "重型弩：扩展装置"},
    {"id": 4012, "name": "卡里姆的形象"},
    {"id": 4013, "name": "紫甲蜂弩"},
    {"id": 4014, "name": "XRA-9"},
    {"id": 5001, "name": "名刀【村正】"},
    {"id": 5002, "name": "怪刀【毫羽】"},
    {"id": 5003, "name": "炽焰赫尔巴努斯"},
    {"id": 5004, "name": "海蒂"},
    {"id": 5005, "name": "剑斩刀：飞柳"},
    {"id": 5006, "name": "斩剑刀：破舞"},
    {"id": 5007, "name": "优衣的短匕首"},
    {"id": 5008, "name": "亚达玛的誓约"},
    {"id": 5009, "name": "图书馆幽灵封印研究会第2型"},
    {"id": 5010, "name": "永霜的沉默"},
    {"id": 5011, "name": "纳斯特朗的碎片"},
    {"id": 5012, "name": "电光一闪"},
]


def inject_custom_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        .hero-box {
            padding: 1.2rem 1.4rem;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(64,72,110,0.28), rgba(25,28,44,0.55));
            border: 1px solid rgba(255,255,255,0.10);
            margin-bottom: 1.2rem;
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .hero-subtitle {
            font-size: 1rem;
            color: rgba(250,250,250,0.78);
            line-height: 1.6;
        }

        .progress-box {
            padding: 0.9rem 1rem;
            border-radius: 14px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 1rem;
            text-align: center;
        }

        .progress-text {
            font-size: 1.05rem;
            font-weight: 700;
        }

        .weapon-name {
            text-align: center;
            font-size: 1.25rem;
            font-weight: 800;
            margin-top: 0.35rem;
            margin-bottom: 0.65rem;
            min-height: 3rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 800;
            margin-top: 0.3rem;
            margin-bottom: 0.75rem;
        }

        .finish-box {
            padding: 1rem 1.2rem;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(40,90,55,0.35), rgba(20,40,25,0.55));
            border: 1px solid rgba(120,255,160,0.18);
            margin-bottom: 1rem;
        }

        .warning-box {
            padding: 1rem 1.2rem;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(120,85,20,0.32), rgba(48,35,10,0.50));
            border: 1px solid rgba(255,210,100,0.20);
            margin-bottom: 1rem;
        }

        div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button {
            border-radius: 12px;
            font-weight: 700;
            min-height: 3rem;
        }

        div[data-testid="stImage"] img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            image-rendering: pixelated;
        }

        .ranking-card {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.035);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.7rem;
        }

        .ranking-header {
            padding: 0.85rem 1rem;
            border-radius: 14px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            font-weight: 800;
            margin-bottom: 0.7rem;
        }

        .rank-badge {
            font-size: 1.4rem;
            font-weight: 800;
            text-align: center;
            margin-top: 0.7rem;
        }

        .rank-name {
            font-size: 1.08rem;
            font-weight: 800;
            margin-top: 0.55rem;
        }

        .rank-stat {
            font-size: 1rem;
            font-weight: 700;
            text-align: center;
            margin-top: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">Sephiria 武器投票站</div>
            <div class="hero-subtitle">
                从随机出现的两把武器中选出你认为更强的一把。<br>
                共进行 50 轮投票，提交后显示社区累计排行榜。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sync_local_voted_state():
    value = local_storage.getItem(LOCAL_VOTED_KEY)
    if "local_voted_flag" not in st.session_state:
        st.session_state.local_voted_flag = None

    if value is not None:
        st.session_state.local_voted_flag = value


def has_local_voted():
    return st.session_state.get("local_voted_flag") == "true"


def mark_local_voted():
    local_storage.setItem(LOCAL_VOTED_KEY, "true")
    st.session_state.local_voted_flag = "true"


def clear_local_voted():
    local_storage.setItem(LOCAL_VOTED_KEY, "false")
    st.session_state.local_voted_flag = "false"


def get_weapon_image_path(weapon_id):
    image_path = IMAGE_DIR / f"{weapon_id}.png"
    if image_path.exists():
        return str(image_path)
    return None


def generate_schedule(weapons, total_votes=50, max_appearances=5):
    weapon_ids = [weapon["id"] for weapon in weapons]
    weapon_map = {weapon["id"]: weapon for weapon in weapons}

    if len(weapon_ids) > total_votes * 2:
        raise ValueError("武器数量太多，当前轮数内无法保证每把至少出现一次。")

    if total_votes * 2 > len(weapon_ids) * max_appearances:
        raise ValueError("当前最大出场限制过低，无法填满全部轮数。")

    appearances = defaultdict(int)
    used_pairs = set()
    schedule = []

    shuffled_ids = weapon_ids[:]
    random.shuffle(shuffled_ids)

    i = 0
    while i + 1 < len(shuffled_ids):
        a = shuffled_ids[i]
        b = shuffled_ids[i + 1]
        pair_key = tuple(sorted((a, b)))

        schedule.append((weapon_map[a], weapon_map[b]))
        used_pairs.add(pair_key)
        appearances[a] += 1
        appearances[b] += 1
        i += 2

    if i < len(shuffled_ids):
        leftover = shuffled_ids[i]

        candidates = [
            wid
            for wid in weapon_ids
            if wid != leftover
            and appearances[wid] < max_appearances
            and tuple(sorted((leftover, wid))) not in used_pairs
        ]

        if not candidates:
            raise ValueError("无法为最后一把武器找到合法对手。")

        min_app = min(appearances[wid] for wid in candidates)
        candidates = [wid for wid in candidates if appearances[wid] == min_app]
        opponent = random.choice(candidates)

        pair_key = tuple(sorted((leftover, opponent)))
        schedule.append((weapon_map[leftover], weapon_map[opponent]))
        used_pairs.add(pair_key)
        appearances[leftover] += 1
        appearances[opponent] += 1

    attempts = 0
    max_attempts = 30000

    while len(schedule) < total_votes and attempts < max_attempts:
        attempts += 1

        available = [wid for wid in weapon_ids if appearances[wid] < max_appearances]
        if len(available) < 2:
            break

        min_app = min(appearances[wid] for wid in available)
        pool_a = [wid for wid in available if appearances[wid] == min_app]
        a = random.choice(pool_a)

        candidates_b = [
            wid
            for wid in available
            if wid != a and tuple(sorted((a, wid))) not in used_pairs
        ]

        if not candidates_b:
            continue

        min_b_app = min(appearances[wid] for wid in candidates_b)
        pool_b = [wid for wid in candidates_b if appearances[wid] == min_b_app]
        b = random.choice(pool_b)

        pair_key = tuple(sorted((a, b)))
        schedule.append((weapon_map[a], weapon_map[b]))
        used_pairs.add(pair_key)
        appearances[a] += 1
        appearances[b] += 1

    if len(schedule) < total_votes:
        raise ValueError("在当前约束下无法生成完整赛程，请放宽限制。")

    return schedule


def reset_vote_state():
    st.session_state.vote_count = 0
    st.session_state.current_round_index = 0
    st.session_state.schedule = generate_schedule(
        weapons,
        total_votes=TOTAL_VOTES,
        max_appearances=MAX_APPEARANCES_PER_WEAPON,
    )
    st.session_state.results = {
        weapon["id"]: {
            "name": weapon["name"],
            "wins": 0,
            "appearances": 0,
        }
        for weapon in weapons
    }
    st.session_state.vote_history = []
    st.session_state.submission_saved = False
    st.session_state.ranking_view = "styled"


def vote(winner_id, loser_id):
    if st.session_state.vote_count >= TOTAL_VOTES:
        return

    left_weapon, right_weapon = st.session_state.schedule[st.session_state.current_round_index]

    st.session_state.results[winner_id]["wins"] += 1
    st.session_state.results[winner_id]["appearances"] += 1
    st.session_state.results[loser_id]["appearances"] += 1

    st.session_state.vote_history.append(
        {
            "round_index": st.session_state.current_round_index + 1,
            "left_weapon_id": left_weapon["id"],
            "right_weapon_id": right_weapon["id"],
            "winner_weapon_id": winner_id,
            "loser_weapon_id": loser_id,
        }
    )

    st.session_state.vote_count += 1
    st.session_state.current_round_index += 1


def get_rank_icon(rank):
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    return f"#{rank}"


def build_community_ranking_dataframe():
    rows = get_community_leaderboard()
    weapon_name_map = {weapon["id"]: weapon["name"] for weapon in weapons}

    ranking_data = []
    for weapon_id, wins, appearances, win_rate in rows:
        ranking_data.append(
            {
                "武器ID": weapon_id,
                "武器名称": weapon_name_map.get(weapon_id, f"未知武器 {weapon_id}"),
                "胜场": wins,
                "出场": appearances,
                "胜率": win_rate,
            }
        )

    if not ranking_data:
        return pd.DataFrame(columns=["武器ID", "武器名称", "胜场", "出场", "胜率"])

    df = pd.DataFrame(ranking_data)
    df.index = df.index + 1
    return df


def render_weapon_card(weapon, opponent, button_key):
    with st.container(border=True):
        image_path = get_weapon_image_path(weapon["id"])

        if image_path:
            img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
            with img_col2:
                st.image(image_path, width=220)
        else:
            st.write("暂无图片")

        st.markdown(
            f'<div class="weapon-name">{weapon["name"]}</div>',
            unsafe_allow_html=True,
        )

        if st.button(f"选择 {weapon['name']}", key=button_key, use_container_width=True):
            vote(weapon["id"], opponent["id"])
            st.rerun()


def render_ranking_board(df):
    st.markdown(
        """
        <div class="ranking-header">
            社区累计排行榜（美化版）
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("当前还没有社区投票数据。")
        return

    for rank, (_, row) in enumerate(df.iterrows(), start=1):
        weapon_id = row["武器ID"]
        weapon_name = row["武器名称"]
        wins = int(row["胜场"])
        appearances = int(row["出场"])
        win_rate = row["胜率"]
        rank_icon = get_rank_icon(rank)
        image_path = get_weapon_image_path(weapon_id)

        st.markdown('<div class="ranking-card">', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns([0.9, 1.1, 3.2, 1.2, 1.2])

        with col1:
            st.markdown(
                f'<div class="rank-badge">{rank_icon}</div>',
                unsafe_allow_html=True,
            )

        with col2:
            if image_path:
                st.image(image_path, width=72)

        with col3:
            st.markdown(
                f'<div class="rank-name">{weapon_name}</div>',
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f'<div class="rank-stat">{wins} / {appearances}</div>',
                unsafe_allow_html=True,
            )
            st.caption("胜场 / 出场")

        with col5:
            st.markdown(
                f'<div class="rank-stat">{win_rate}%</div>',
                unsafe_allow_html=True,
            )
            st.caption("胜率")

        st.markdown("</div>", unsafe_allow_html=True)


def render_simple_ranking_table(df):
    if df.empty:
        st.info("当前还没有社区投票数据。")
        return

    display_df = df.copy()
    display_df = display_df.drop(columns=["武器ID"])
    st.dataframe(display_df, use_container_width=True, height=650)


def render_admin_tools():
    admin_code = st.secrets.get("admin_reset_code", "")

    with st.expander("管理员工具"):
        st.caption("仅供你自己测试、修复网站和管理数据时使用。")
        entered_code = st.text_input("管理员口令", type="password", key="admin_code_input")

        if st.button("清除本地已投票标记并重置当前浏览器", use_container_width=True):
            if admin_code and entered_code == admin_code:
                clear_local_voted()
                reset_vote_state()
                st.success("已清除本地标记并重置当前浏览器。")
                st.rerun()
            elif not admin_code:
                st.error("当前没有配置 admin_reset_code。")
            else:
                st.error("管理员口令不正确。")

        if st.button("清空全部社区投票数据", use_container_width=True):
            if admin_code and entered_code == admin_code:
                clear_all_votes()
                st.success("全部社区投票数据已清空。")
                st.rerun()
            elif not admin_code:
                st.error("当前没有配置 admin_reset_code。")
            else:
                st.error("管理员口令不正确。")


init_db()
inject_custom_css()
render_hero()
sync_local_voted_state()

if "schedule" not in st.session_state:
    st.session_state.schedule = generate_schedule(
        weapons,
        total_votes=TOTAL_VOTES,
        max_appearances=MAX_APPEARANCES_PER_WEAPON,
    )

if "current_round_index" not in st.session_state:
    st.session_state.current_round_index = 0

if "vote_count" not in st.session_state:
    st.session_state.vote_count = 0

if "results" not in st.session_state:
    st.session_state.results = {
        weapon["id"]: {
            "name": weapon["name"],
            "wins": 0,
            "appearances": 0,
        }
        for weapon in weapons
    }

if "vote_history" not in st.session_state:
    st.session_state.vote_history = []

if "submission_saved" not in st.session_state:
    st.session_state.submission_saved = False

if "ranking_view" not in st.session_state:
    st.session_state.ranking_view = "styled"

is_finished = st.session_state.vote_count >= TOTAL_VOTES
already_voted_locally = has_local_voted()

if is_finished and not st.session_state.submission_saved:
    save_submission(st.session_state.vote_history)
    st.session_state.submission_saved = True
    mark_local_voted()

if already_voted_locally and not is_finished:
    st.markdown(
        """
        <div class="warning-box">
            <div class="section-title">你已经提交过投票</div>
            当前浏览器已记录为“已完成投票”，因此默认不能重复提交。
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_col1, top_col2 = st.columns([1, 1])

    with top_col1:
        if st.session_state.ranking_view == "styled":
            if st.button("切换到精简版", use_container_width=True):
                st.session_state.ranking_view = "simple"
                st.rerun()
        else:
            if st.button("切换到美化版", use_container_width=True):
                st.session_state.ranking_view = "styled"
                st.rerun()

    with top_col2:
        render_admin_tools()

    st.markdown('<div class="section-title">社区累计排行榜</div>', unsafe_allow_html=True)

    df = build_community_ranking_dataframe()

    if st.session_state.ranking_view == "styled":
        render_ranking_board(df)
    else:
        render_simple_ranking_table(df)

elif not is_finished:
    left_weapon, right_weapon = st.session_state.schedule[st.session_state.current_round_index]

    st.markdown(
        f"""
        <div class="progress-box">
            <div class="progress-text">当前进度：{st.session_state.vote_count} / {TOTAL_VOTES} 轮</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    gap_col1, col1, mid_col, col2, gap_col2 = st.columns([0.2, 1, 0.15, 1, 0.2])

    with col1:
        render_weapon_card(left_weapon, right_weapon, "left_vote")

    with mid_col:
        st.markdown(
            "<div style='text-align:center; font-size:1.8rem; font-weight:800; margin-top:10rem;'>VS</div>",
            unsafe_allow_html=True,
        )

    with col2:
        render_weapon_card(right_weapon, left_weapon, "right_vote")

    st.write("")

    st.caption(
        f"赛程规则：50轮内同一对不会重复；每把武器至少出现1次；每把武器最多出现{MAX_APPEARANCES_PER_WEAPON}次。"
    )

    render_admin_tools()

else:
    st.markdown(
        f"""
        <div class="finish-box">
            <div class="section-title">投票结束</div>
            你已经完成了 {TOTAL_VOTES} 轮投票，本次结果已计入社区总榜。
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_col1, top_col2 = st.columns([1, 1])

    with top_col1:
        if st.session_state.ranking_view == "styled":
            if st.button("切换到精简版", use_container_width=True):
                st.session_state.ranking_view = "simple"
                st.rerun()
        else:
            if st.button("切换到美化版", use_container_width=True):
                st.session_state.ranking_view = "styled"
                st.rerun()

    with top_col2:
        render_admin_tools()

    st.markdown('<div class="section-title">社区累计排行榜</div>', unsafe_allow_html=True)

    df = build_community_ranking_dataframe()

    if st.session_state.ranking_view == "styled":
        render_ranking_board(df)
    else:
        render_simple_ranking_table(df)