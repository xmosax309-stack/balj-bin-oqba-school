# -*- coding: utf-8 -*-
"""تطبيق إدارة بيانات الهيئة التعليمية — مدرسة بلج بن عقبة للتعليم الأساسي
قاعدة بيانات SQLite + واجهة Streamlit عربية (RTL)
"""
import pandas as pd
import streamlit as st

import database as db

st.set_page_config(
    page_title="مدرسة بلج بن عقبة | قاعدة البيانات",
    page_icon=":material/school:",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()

# ═══════════════════════════ التنسيقات (RTL + التصميم) ═══════════════════════════
st.html("""
<style>
[data-testid="stAppViewContainer"], [data-testid="stSidebar"] { direction: rtl; }
[data-testid="stAppViewContainer"] .block-container { padding-top: 2.4rem; max-width: 1280px; }

/* بطاقة الترويسة */
.hero { border-radius: 18px; padding: 24px 28px; color: #F2FAF7;
        background: linear-gradient(120deg, #0D3B33 0%, #0E5949 55%, #0E7C66 100%);
        box-shadow: 0 12px 32px rgba(13,59,51,.28); border: 1px solid #1E5C50; }
.hero-top { display: flex; justify-content: space-between; align-items: center; gap: 18px; flex-wrap: wrap; }
.hero h1 { margin: 0; font-size: 1.65rem; font-weight: 800; color: #FFFFFF; }
.hero .sub { opacity: .85; margin-top: 4px; font-size: .95rem; }
.hero .code { background: rgba(201,162,39,.16); border: 1px solid rgba(201,162,39,.6);
              border-radius: 14px; padding: 10px 20px; text-align: center; min-width: 112px; }
.hero .code .num { font-size: 1.55rem; font-weight: 800; color: #EED688; line-height: 1.15; }
.hero .code .lbl { font-size: .78rem; color: #D9E9E4; }
.hero-meta { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }
.hero-meta span { background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.24);
                  padding: 5px 13px; border-radius: 999px; font-size: .85rem; }
.hero .royal { margin-top: 12px; font-size: .88rem; color: #CFE6DF; }

/* بطاقات المؤشرات */
[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #E2EDE8; border-radius: 16px;
                           padding: 14px 18px; box-shadow: 0 4px 14px rgba(13,59,51,.06); }
[data-testid="stMetricLabel"] p { font-weight: 700; color: #47665D; font-size: .92rem; }
[data-testid="stMetricValue"] { color: #0D3B33; font-weight: 800; }

/* الجداول */
.tbl-wrap { overflow-x: auto; border: 1px solid #E2EDE8; border-radius: 14px; background: #FFFFFF;
            box-shadow: 0 4px 14px rgba(13,59,51,.05); }
table.tbl { width: 100%; border-collapse: collapse; direction: rtl; font-size: .92rem; }
table.tbl thead th { background: #0D3B33; color: #F2FAF7; text-align: right; padding: 11px 14px;
                     font-weight: 700; white-space: nowrap; border-bottom: 2px solid #C9A227; }
table.tbl thead th:first-child { border-top-right-radius: 13px; }
table.tbl thead th:last-child { border-top-left-radius: 13px; }
table.tbl tbody td { padding: 9px 14px; border-bottom: 1px solid #EEF4F1; text-align: right; vertical-align: middle; }
table.tbl tbody tr:nth-child(even) { background: #F8FBF9; }
table.tbl tbody tr:hover { background: #EDF7F2; }
table.tbl tbody tr:last-child td { border-bottom: none; }
.muted { color: #9FB2AC; }
.num { font-variant-numeric: tabular-nums; }

/* الشارات */
.chip { display: inline-block; padding: 3px 12px; border-radius: 999px; font-size: .78rem;
        font-weight: 700; white-space: nowrap; border: 1px solid transparent; }
.chip-teal   { background: #E1F3EE; color: #0B6B55; border-color: #BDE3D8; }
.chip-gold   { background: #FBF3DF; color: #8A6A1F; border-color: #EDDFB6; }
.chip-blue   { background: #E7F0FA; color: #1D5FA8; border-color: #C9DDF3; }
.chip-violet { background: #F1EAFA; color: #6B3FA0; border-color: #DDCBF3; }
.chip-rose   { background: #FBEAF0; color: #A63668; border-color: #F2CFDD; }
.chip-green  { background: #E8F6EC; color: #1F7A3D; border-color: #CBE9D6; }
.chip-gray   { background: #F0F3F5; color: #5A6B72; border-color: #DDE4E8; }

/* عناوين الأقسام */
.sec-title { display: flex; align-items: center; gap: 10px; margin: 8px 0 2px; }
.sec-title .bar { width: 6px; height: 26px; border-radius: 6px;
                  background: linear-gradient(#C9A227, #0E7C66); }
.sec-title h3 { margin: 0; color: #0D3B33; font-weight: 800; font-size: 1.25rem; }

/* صندوق أدوات البحث */
div[data-testid="stTextInput"] input { text-align: right; }

/* الرسوم البيانية (Vega) تُعرض دائماً بشكل LTR حتى لا تختل النصوص */
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] { direction: ltr; }

/* اتجاه صحيح لبطاقات المؤشرات */
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] { direction: rtl; }
</style>
""")

# ═══════════════════════════ أدوات مساعدة ═══════════════════════════
SECTION_CHIP = {
    "الهيئة الإدارية": "chip-gold",
    "التربية الإسلامية": "chip-green",
    "اللغة العربية": "chip-teal",
    "الدراسات الاجتماعية": "chip-blue",
    "مواد العلوم": "chip-violet",
    "اللغة الإنجليزية": "chip-rose",
    "المهارات الفردية": "chip-gold",
    "الرياضيات": "chip-blue",
    "التربية الخاصة": "chip-teal",
    "الحراس": "chip-gray",
    "العمال": "chip-gray",
    "الممرضة": "chip-rose",
}

LTR_COLUMNS = {"رقم الملف", "رقم الهاتف", "الرقم المدني", "تاريخ التعيين", "هاتف السائق", "هاتف المشرف"}


def _blank(v):
    return v is None or (isinstance(v, float) and pd.isna(v)) or str(v).strip() in ("", "nan", "None")


def table_html(df: pd.DataFrame, chip_columns=None) -> str:
    chip_columns = chip_columns or {}
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if _blank(v):
                cells.append('<td><span class="muted">—</span></td>')
                continue
            s = str(v).strip()
            if isinstance(v, float) and float(v).is_integer():
                s = str(int(v))
            if col in chip_columns:
                chip = chip_columns[col]
                cls = chip(s) if callable(chip) else chip
                cells.append(f'<td><span class="chip {cls}">{s}</span></td>')
            elif col in LTR_COLUMNS:
                cells.append(f'<td><span class="num" dir="ltr">{s}</span></td>')
            else:
                cells.append(f"<td>{s}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<div class="tbl-wrap"><table class="tbl">'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def section_title(text: str):
    st.html(f'<div class="sec-title"><span class="bar"></span><h3>{text}</h3></div>')


def search_filter(df: pd.DataFrame, query: str) -> pd.DataFrame:
    query = (query or "").strip()
    if not query:
        return df
    text = df.fillna("").astype(str)
    mask = text.apply(lambda r: r.str.contains(query, case=False, regex=False, na=False).any(), axis=1)
    return df[mask]


def csv_download(df: pd.DataFrame, label: str, file_name: str):
    st.download_button(
        label,
        df.to_csv(index=False).encode("utf-8-sig"),
        file_name=file_name,
        mime="text/csv",
        icon=":material/download:",
    )


def with_index(df: pd.DataFrame, start=1) -> pd.DataFrame:
    out = df.reset_index(drop=True).copy()
    out.insert(0, "م", range(start, start + len(out)))
    return out


def get_stat(stats: pd.DataFrame, category: str, label: str, default=0):
    try:
        return int(stats.loc[(stats["الفئة"] == category) & (stats["البند"] == label), "القيمة"].iloc[0])
    except (IndexError, KeyError, ValueError):
        return default


def hero(info: dict):
    st.html(f"""
    <div class="hero">
      <div class="hero-top">
        <div>
          <h1>{info.get("name", "المدرسة")}</h1>
          <div class="sub">{info.get("ministry", "")}</div>
        </div>
        <div class="code">
          <div class="num">{info.get("code", "—")}</div>
          <div class="lbl">رمز المدرسة</div>
        </div>
      </div>
      <div class="hero-meta">
        <span>{info.get("year", "")}</span>
        <span>مدير المدرسة: {info.get("director", "")}</span>
      </div>
      <div class="royal">تحت الرعاية السامية لحضرة صاحب الجلالة السلطان هيثم بن طارق المعظم — حفظه الله ورعاه</div>
    </div>
    """)


# ═══════════════════════════ الصفحات ═══════════════════════════
def page_home():
    v = db.db_version()
    info = db.load_school_info(v)
    stats = db.load_stats(v)
    staff = db.load_table("staff", v)

    hero(info)

    guards = get_stat(stats, "الكادر", "الحراس") or len(staff[staff["الفئة"] == "حارس"])
    workers = get_stat(stats, "الكادر", "العمال") or len(staff[staff["الفئة"] == "عامل"])
    sp_total = get_stat(stats, "الحافلات", "حافلات التربية الخاصة (فكري)") + get_stat(
        stats, "الحافلات", "حافلات التربية الخاصة (سمعي)"
    )

    with st.container(horizontal=True):
        st.metric("طلبة المدرسة", get_stat(stats, "الطلبة", "الإجمالي"), border=True, icon=":material/groups:")
        st.metric("الكادر التعليمي", get_stat(stats, "الكادر", "المعلمون"), border=True, icon=":material/menu_book:")
        st.metric("الهيئة الإدارية", get_stat(stats, "الكادر", "الهيئة الإدارية"), border=True, icon=":material/workspace_premium:")
        st.metric("الشعب الدراسية", get_stat(stats, "الشعب", "الإجمالي"), border=True, icon=":material/meeting_room:")

    with st.container(horizontal=True):
        st.metric("طلبة التربية الخاصة", get_stat(stats, "التربية الخاصة", "الإجمالي"), border=True, icon=":material/accessibility_new:")
        st.metric("الحافلات المدرسية", get_stat(stats, "الحافلات", "حافلات عامة"), border=True, icon=":material/directions_bus:")
        st.metric("حافلات التربية الخاصة", sp_total, border=True, icon=":material/accessible:")
        st.metric("الحراس والعمال", guards + workers, border=True, icon=":material/engineering:")

    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("توزيع الطلبة على الصفوف")
            grade_df = stats[(stats["الفئة"] == "الطلبة") & (stats["البند"] != "الإجمالي")]
            st.bar_chart(grade_df, x="البند", y="القيمة", x_label="الصف", y_label="عدد الطلبة", height=270)
    with c2:
        with st.container(border=True):
            st.subheader("الشعب الدراسية")
            sect_df = stats[(stats["الفئة"] == "الشعب") & (stats["البند"] != "الإجمالي")]
            st.bar_chart(sect_df, x="البند", y="القيمة", x_label="الصف", y_label="عدد الشعب", height=270)

    c3, c4 = st.columns(2)
    with c3:
        with st.container(border=True):
            st.subheader("توزيع الكادر التعليمي حسب الأقسام")
            teach = staff[staff["الفئة"] == "معلم"]
            by_section = teach.groupby("القسم", sort=False).size().reset_index(name="عدد المعلمين")
            st.bar_chart(by_section, x="القسم", y="عدد المعلمين", horizontal=True,
                         x_label="عدد المعلمين", y_label="", height=330)
    with c4:
        with st.container(border=True):
            st.subheader("طلبة التربية الخاصة")
            sp_df = stats[(stats["الفئة"] == "التربية الخاصة") & (stats["البند"] != "الإجمالي")]
            if not sp_df.empty:
                import altair as alt

                base = alt.Chart(sp_df)
                arcs = base.mark_arc(innerRadius=58, outerRadius=90, stroke="#FBFDFC", strokeWidth=2).encode(
                    theta=alt.Theta("القيمة", stack=True),
                    color=alt.Color("البند", scale=alt.Scale(range=["#0E7C66", "#C9A227"]),
                                    legend=alt.Legend(orient="bottom", title=None)),
                    tooltip=[alt.Tooltip("البند", title="الفئة"), alt.Tooltip("القيمة", title="العدد")],
                )
                labels = base.mark_text(radius=112, size=13, color="#17332C").encode(
                    theta=alt.Theta("القيمة", stack=True), text=alt.Text("القيمة")
                )
                st.altair_chart((arcs + labels).properties(height=270))

    st.write("")
    c5, c6 = st.columns(2)
    with c5:
        with st.container(border=True):
            st.subheader("رؤية المدرسة")
            st.write(info.get("vision", ""))
    with c6:
        with st.container(border=True):
            st.subheader("رسالة المدرسة")
            st.write(info.get("mission", ""))

    st.caption("قاعدة بيانات مدرسة بلج بن عقبة — أُعدت من ملف بيانات الهيئة التعليمية للعام الدراسي 2026/2027")


def page_admin():
    v = db.db_version()
    staff = db.load_table("staff", v)
    admins = staff[staff["الفئة"] == "إداري"].copy()

    section_title("الهيئة الإدارية والقيادية")
    st.caption(f"عدد أعضاء الهيئة الإدارية: {len(admins)}")

    c1, c2 = st.columns([3, 1])
    query = c1.text_input("بحث", placeholder="ابحث بالاسم أو الوظيفة أو رقم الملف أو الهاتف...",
                          icon=":material/search:", label_visibility="collapsed")
    with c2:
        csv_download(staff[staff["الفئة"] == "إداري"],
                     "تنزيل القائمة (CSV)", "الهيئة_الإدارية.csv")

    df = search_filter(admins, query)
    if df.empty:
        st.info("لا توجد نتائج مطابقة للبحث.")
        return

    cols = ["الاسم", "الوظيفة", "رقم الملف", "رقم الهاتف", "تاريخ التعيين", "ملاحظات"]
    st.html(table_html(with_index(df[cols]), chip_columns={"ملاحظات": "chip-gold"}))
    st.caption(f"عدد النتائج: {len(df)}")


def page_teachers():
    v = db.db_version()
    staff = db.load_table("staff", v)
    teach = staff[staff["الفئة"] == "معلم"].copy()

    section_title("الكادر التعليمي")
    options = ["الكل"] + [str(s) for s in pd.unique(teach["القسم"])]
    selected = st.pills("تصفية حسب القسم", options, selection_mode="single", default="الكل",
                        label_visibility="collapsed")
    selected = selected or "الكل"

    c1, c2 = st.columns([3, 1])
    query = c1.text_input("بحث", placeholder="ابحث بالاسم أو الوظيفة أو رقم الملف أو الهاتف...",
                          icon=":material/search:", label_visibility="collapsed")
    with c2:
        csv_download(teach if selected == "الكل" else teach[teach["القسم"] == selected],
                     "تنزيل القائمة (CSV)", f"الكادر_التعليمي_{selected}.csv")

    df = teach if selected == "الكل" else teach[teach["القسم"] == selected]
    df = search_filter(df, query)
    if df.empty:
        st.info("لا توجد نتائج مطابقة للبحث.")
        return

    cols = ["الاسم"] + (["القسم"] if selected == "الكل" else []) + \
           ["الوظيفة", "رقم الملف", "رقم الهاتف", "تاريخ التعيين", "ملاحظات"]
    chips = {"ملاحظات": "chip-gold"}
    if selected == "الكل":
        chips["القسم"] = lambda s: SECTION_CHIP.get(s, "chip-gray")
    st.html(table_html(with_index(df[cols]), chip_columns=chips))
    st.caption(f"عدد المعلمين المعروضين: {len(df)} — ملاحظة: المعلم المثبّت «انتداب» غير محتسب ضمن إحصائية المعلمين الرسمية (71)")


def page_buses():
    v = db.db_version()
    buses = db.load_table("buses", v)
    special = db.load_table("special_buses", v)

    section_title("النقل المدرسي")
    intellectual = special[special["البرنامج"] == "فكري"]
    hearing = special[special["البرنامج"] == "سمعي"]

    with st.container(horizontal=True):
        st.metric("حافلات عامة", len(buses), border=True, icon=":material/directions_bus:")
        st.metric("حافلات فكرية", len(intellectual), border=True, icon=":material/directions_bus_filled:")
        st.metric("حافلات سمعية", len(hearing), border=True, icon=":material/directions_bus_filled:")
        st.metric("طلبة النقل (فكري)", int(intellectual["عدد الطلبة"].sum()), border=True, icon=":material/child_care:")
        st.metric("طلبة النقل (سمعي)", int(hearing["عدد الطلبة"].sum()), border=True, icon=":material/child_care:")

    kind = st.segmented_control(
        "نوع الحافلات",
        ["حافلات عامة", "التربية الخاصة (فكري)", "التربية الخاصة (سمعي)"],
        default="حافلات عامة",
        label_visibility="collapsed",
    )
    kind = kind or "حافلات عامة"

    query = st.text_input("بحث", placeholder="ابحث باسم السائق أو المالك أو المشرف أو رقم الحافلة...",
                          icon=":material/search:", label_visibility="collapsed")

    if kind == "حافلات عامة":
        df = search_filter(buses, query)
        if df.empty:
            st.info("لا توجد نتائج مطابقة للبحث.")
            return
        cols = ["رقم الحافلة", "اسم السائق", "هاتف السائق", "اسم المالك",
                "طلبة النقلة الأولى", "طلبة النقلة الثانية"]
        st.html(table_html(with_index(df[cols])))
        st.caption(f"عدد الحافلات المعروضة: {len(df)}")
    else:
        program = "فكري" if "فكري" in kind else "سمعي"
        df = search_filter(special[special["البرنامج"] == program], query)
        if df.empty:
            st.info("لا توجد نتائج مطابقة للبحث.")
            return
        cols = ["اسم السائق", "هاتف السائق", "اسم المشرف", "هاتف المشرف", "عدد الطلبة"]
        st.html(table_html(with_index(df[cols])))
        st.caption(f"عدد الحافلات المعروضة: {len(df)} — إجمالي الطلبة: {int(special[special['البرنامج'] == program]['عدد الطلبة'].sum())}")


def page_workers():
    v = db.db_version()
    staff = db.load_table("staff", v)
    guards = staff[staff["الفئة"] == "حارس"].copy()
    workers = staff[staff["الفئة"] == "عامل"].copy()

    section_title("الحراس والعمال")
    query = st.text_input("بحث", placeholder="ابحث بالاسم أو الرقم المدني أو الهاتف...",
                          icon=":material/search:", label_visibility="collapsed")

    cols = ["الاسم", "رقم الملف", "رقم الهاتف", "الرقم المدني"]

    g = search_filter(guards, query)
    st.subheader(f"الحراس ({len(guards)})")
    if g.empty:
        st.info("لا توجد نتائج مطابقة للبحث في الحراس.")
    else:
        st.html(table_html(with_index(g[cols])))

    w = search_filter(workers, query)
    st.subheader(f"العمال ({len(workers)})")
    if w.empty:
        st.info("لا توجد نتائج مطابقة للبحث في العمال.")
    else:
        st.html(table_html(with_index(w[cols])))


def page_services():
    v = db.db_version()
    staff = db.load_table("staff", v)
    coop = db.load_table("cooperative", v)

    section_title("ممرضة المدرسة والجمعية التعاونية")

    nurse = staff[staff["الفئة"] == "ممرضة"]
    st.subheader("ممرضة المدرسة")
    if nurse.empty:
        st.info("لا توجد بيانات ممرضة مسجلة.")
    else:
        n = nurse.iloc[0]
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{n['الاسم']}**")
                st.caption(n["الوظيفة"] or "ممرضة المدرسة")
            with c2:
                st.markdown(f'<div style="text-align:left; font-weight:700; color:#0D3B33;">'
                            f'<span class="num" dir="ltr">{n["رقم الهاتف"]}</span></div>',
                            unsafe_allow_html=True)

    st.subheader("الجمعية التعاونية")
    is_empty = coop.fillna("").astype(str).apply(lambda r: r.str.strip().eq("").all(), axis=1).all()
    if is_empty:
        st.info("لا توجد بيانات مسجلة للمستأجر حالياً — يمكن إضافتها من صفحة «إدارة البيانات».")
    else:
        st.html(table_html(with_index(coop)))


def page_manage():
    v = db.db_version()
    section_title("إدارة قاعدة البيانات")
    st.caption("عدّل الجداول مباشرة (إضافة / تعديل / حذف صفوف) ثم اضغط «حفظ التعديلات». "
               "كل التغييرات تُخزَّن في ملف قاعدة البيانات school.db")

    key = st.selectbox("اختر الجدول", list(db.TABLE_TITLES), format_func=lambda k: db.TABLE_TITLES[k])
    df = db.load_table(key, v)

    column_config = {}
    if key == "buses":
        column_config = {
            "رقم الحافلة": st.column_config.NumberColumn("رقم الحافلة", format="%d"),
            "طلبة النقلة الأولى": st.column_config.NumberColumn("طلبة النقلة الأولى", format="%d"),
            "طلبة النقلة الثانية": st.column_config.NumberColumn("طلبة النقلة الثانية", format="%d"),
        }
    elif key == "special_buses":
        column_config = {
            "عدد الطلبة": st.column_config.NumberColumn("عدد الطلبة", format="%d"),
        }

    edited = st.data_editor(df, num_rows="dynamic", hide_index=True, column_config=column_config,
                            key=f"editor_{key}")

    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        if st.button("حفظ التعديلات", type="primary", icon=":material/save:"):
            db.save_table(key, edited)
            st.session_state.pop(f"editor_{key}", None)
            st.toast("تم حفظ التعديلات في قاعدة البيانات", icon=":material/check_circle:")
            st.rerun()
    with c2:
        if st.button("استعادة الأصلية", icon=":material/restart_alt:"):
            db.reseed_table(key)
            st.session_state.pop(f"editor_{key}", None)
            st.toast("تمت استعادة البيانات الأصلية للجدول", icon=":material/history:")
            st.rerun()
    with c3:
        csv_download(df, "تنزيل CSV", f"{key}.csv")
    with c4:
        backup = open(db.DB_PATH, "rb").read()
        st.download_button("تنزيل نسخة احتياطية من قاعدة البيانات", backup,
                           file_name="school_backup.db", mime="application/octet-stream",
                           icon=":material/database:")

    st.divider()
    st.subheader("بيانات المدرسة العامة")
    info = db.load_school_info(v)
    with st.form("school_info_form"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("اسم المدرسة", info.get("name", ""))
        code = c2.text_input("رمز المدرسة", info.get("code", ""))
        year = c3.text_input("العام الدراسي", info.get("year", ""))
        director = st.text_input("مدير المدرسة", info.get("director", ""))
        vision = st.text_area("رؤية المدرسة", info.get("vision", ""))
        mission = st.text_area("رسالة المدرسة", info.get("mission", ""))
        if st.form_submit_button("حفظ بيانات المدرسة", type="primary", icon=":material/save:"):
            db.save_school_info({
                "name": name, "code": code, "year": year, "director": director,
                "vision": vision, "mission": mission,
            })
            st.toast("تم حفظ بيانات المدرسة", icon=":material/check_circle:")
            st.rerun()

    st.divider()
    with st.popover("منطقة الخطر"):
        st.warning("إعادة التعيين تحذف كل التعديلات نهائياً وتعيد البيانات الأصلية لجميع الجداول.")
        if st.button("إعادة تعيين قاعدة البيانات بالكامل", type="primary", icon=":material/delete_forever:"):
            db.reset_db()
            st.session_state.clear()
            st.toast("تمت إعادة تعيين قاعدة البيانات", icon=":material/restart_alt:")
            st.rerun()


# ═══════════════════════════ التنقل ═══════════════════════════
pages = {
    "عام": [
        st.Page(page_home, title="لوحة المعلومات", icon=":material/dashboard:", default=True),
    ],
    "الكادر": [
        st.Page(page_admin, title="الهيئة الإدارية", icon=":material/workspace_premium:"),
        st.Page(page_teachers, title="الكادر التعليمي", icon=":material/menu_book:"),
    ],
    "الخدمات والمرافق": [
        st.Page(page_buses, title="الحافلات والنقل", icon=":material/directions_bus:"),
        st.Page(page_workers, title="الحراس والعمال", icon=":material/handyman:"),
        st.Page(page_services, title="الممرضة والجمعية", icon=":material/local_hospital:"),
    ],
    "الإدارة": [
        st.Page(page_manage, title="إدارة البيانات", icon=":material/edit_note:"),
    ],
}

navigation = st.navigation(pages)

with st.sidebar:
    st.caption("قاعدة بيانات المدرسة — نسخة 2026/2027 · ملف SQLite محلي")

navigation.run()
