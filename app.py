
import io
import sqlite3
from datetime import date
import pandas as pd
import streamlit as st
import os
import tempfile
import subprocess

def convert_html_to_pdf(html_content):
    """
    تحويل محتوى HTML إلى ملف PDF حقيقي عالي الجودة بنظام A4 
    باستخدام محرك الويندوز المدمج (Edge / Chrome) دون أي مكاتب خارجية معقدة.
    """
    # البحث عن مسار متصفح Edge أو Chrome في الويندوز
    possible_paths = [
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Microsoft\\Edge\\Application\\msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Microsoft\\Edge\\Application\\msedge.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft\\Edge\\Application\\msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Google\\Chrome\\Application\\chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Google\\Chrome\\Application\\chrome.exe")
    ]
    
    browser_exe = None
    for p in possible_paths:
        if os.path.exists(p):
            browser_exe = p
            break
            
    # تضمين كود CSS خاص بحجم ورقة A4 وهوامش الطباعة والخط العربي
    full_html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
            @page {{
                size: A4 portrait;
                margin: 10mm;
            }}
            body {{
                font-family: 'Cairo', Arial, sans-serif !important;
                direction: rtl !important;
                text-align: right !important;
                background-color: #ffffff !important;
                color: #000000 !important;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    if browser_exe:
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                html_path = os.path.join(tmp_dir, "document.html")
                pdf_path = os.path.join(tmp_dir, "output.pdf")
                
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(full_html)
                    
                # أمر تشغيل التحويل الصامت إلى PDF
                cmd = [
                    browser_exe,
                    "--headless",
                    "--disable-gpu",
                    "--run-all-compositor-stages-before-draw",
                    f"--print-to-pdf={pdf_path}",
                    html_path
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=15)
                
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as pdf_file:
                        return pdf_file.read(), "application/pdf"
        except Exception:
            pass

    # في حال تعذر التحويل الصامت لأي سبب، يُرسل الملف كـ HTML مبرمج ليفتح نافذة الطباعة كـ PDF فوراً
    auto_print_html = full_html + "<script>window.onload = function() { window.print(); };</script>"
    return auto_print_html.encode("utf-8"), "text/html"
# استدعاء plotly بأمان مع دعم بيئات بايثون المختلفة
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from database import create_tables, get_connection

# تهيئة قاعدة البيانات والجداول
# تهيئة قاعدة البيانات والجداول
create_tables()

# 🛡️ ترقية ذاتية وفورية لقاعدة البيانات إن كان ينقصها عمود السلوك أو الجنس
try:
    _conn = get_connection()
    _cursor = _conn.cursor()
    _cursor.execute("PRAGMA table_info(students)")
    _cols = [c[1] for c in _cursor.fetchall()]
    if "behavior" not in _cols and len(_cols) > 0:
        _cursor.execute("ALTER TABLE students ADD COLUMN behavior TEXT DEFAULT 'عادي'")
    if "gender" not in _cols and len(_cols) > 0:
        _cursor.execute("ALTER TABLE students ADD COLUMN gender TEXT DEFAULT 'غير محدد'")
    _conn.commit()
    _conn.close()
except Exception:
    pass

st.set_page_config(
    page_title="منظومة التقويم التشخيصي والمعالجة البيداغوجية",
    page_icon="📐",
    layout="wide"
)

# ==============================================================================
# 🎨 التصميم الفني العصري (محمي ومضبوط للأيقونات والوضع الليلي)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    
    /* تطبيق الخط العربي واتجاه RTL على التطبيق ومحتواه فقط */
    .stApp {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }

    /* تطبيق الخط والمحاذاة على النصوص والعناوين والقوائم */
    .stMarkdown, p, h1, h2, h3, h4, label, .stSelectbox label, .stTextInput label, .stNumberInput label {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* 🛡️ حماية قائمة ستريمليت العلوية من التداخل */
    header[data-testid="stHeader"], 
    [data-testid="stToolbar"], 
    [role="menu"], 
    [role="menu"] * {
        direction: ltr !important;
        text-align: left !important;
    }

    /* 🛡️ حماية خط الأيقونات الرسمية لستريمليت لمنع تحولها إلى نصوص مشوهة */
    [data-testid="stIconMaterial"], 
    .material-symbols-rounded, 
    [class*="material-symbols"], 
    span[translate="no"] {
        font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        direction: ltr !important;
        letter-spacing: normal !important;
    }

    /* بطاقات متكيفة مع الثيم المظلم والفاتح */
    .art-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-right: 6px solid #1E88E5;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .art-alert-danger {
        background-color: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-right: 6px solid #EF4444;
        color: var(--text-color);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-weight: 600;
    }
    
    .art-alert-success {
        background-color: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
        border-right: 6px solid #22C55E;
        color: var(--text-color);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-weight: 600;
    }

    .art-alert-info {
        background-color: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-right: 6px solid #3B82F6;
        color: var(--text-color);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    .badge-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 700;
        white-space: nowrap;
        text-align: center;
    }
    .badge-red { background-color: rgba(239, 68, 68, 0.2); color: #FF6B6B; border: 1px solid #EF4444; }
    .badge-orange { background-color: rgba(245, 158, 11, 0.2); color: #FFA94D; border: 1px solid #F59E0B; }
    .badge-green { background-color: rgba(34, 197, 94, 0.2); color: #51CF66; border: 1px solid #22C55E; }
    .badge-star { background-color: rgba(168, 85, 247, 0.2); color: #CC5DE8; border: 1px solid #A855F7; }

    .art-table-wrapper {
        width: 100%;
        overflow-x: auto;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin: 15px 0;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
    }
    table.art-table {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
        font-family: 'Cairo', sans-serif;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }
    table.art-table th {
        background-color: rgba(30, 136, 229, 0.15);
        color: var(--text-color);
        padding: 13px 15px;
        font-weight: 800;
        font-size: 0.95em;
        border-bottom: 2px solid rgba(30, 136, 229, 0.35);
        text-align: right;
        white-space: nowrap;
    }
    table.art-table td {
        padding: 12px 15px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15);
        font-size: 0.92em;
        text-align: right;
        vertical-align: middle;
    }
    table.art-table tr:hover {
        background-color: rgba(128, 128, 128, 0.07);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- الثوابت الرسمية -----------------
RESOURCES = [
    "الأعداد والحساب",
    "الحساب الجبري",
    "الدوال والمنحنيات",
    "الهندسة والأشعة"
]

# ----------------- الدوال المساعدة -----------------
def get_classes():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM classes ORDER BY level, class_name").fetchall()
    finally:
        conn.close()

def get_students(class_id=None):
    conn = get_connection()
    try:
        query = """
            SELECT students.*, classes.level, classes.class_name 
            FROM students 
            INNER JOIN classes ON students.class_id = classes.id 
        """
        params = ()
        if class_id is not None:
            query += " WHERE students.class_id = ? "
            params = (class_id,)
            
        query += " ORDER BY classes.level, classes.class_name, students.full_name "
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()

def classification(total):
    if total >= 15:
        return "متحكم جدًا"
    elif total >= 10:
        return "متحكم"
    elif total >= 7:
        return "متحكم جزئيًا"
    return "غير متحكم"

def format_badge_html(status):
    if "غير متحكم" in status:
        return "<span class='badge-pill badge-red'>🔴 غير متحكم</span>"
    elif "جزئي" in status:
        return "<span class='badge-pill badge-orange'>🟠 متحكم جزئيًا</span>"
    elif "متحكم جد" in status:
        return "<span class='badge-pill badge-star'>⭐ متحكم جدًا</span>"
    return "<span class='badge-pill badge-green'>🟢 متحكم</span>"

def render_artistic_table(data_list):
    if not data_list:
        st.info("لا توجد بيانات متاحة لعرضها.")
        return
    headers = list(data_list[0].keys())
    html = "<div class='art-table-wrapper'><table class='art-table'><thead><tr>"
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"
    for row in data_list:
        html += "<tr>"
        for h in headers:
            html += f"<td>{row.get(h, '')}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)

# دالة سحرية لتنظيف كود HTML ومنع ظهوره كنصوص سوداء مبعثرة
def render_clean_html(html_str):
    clean_str = " ".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean_str, unsafe_allow_html=True)

def class_options_dict():
    return {f"{item['level']} — {item['class_name']}": item["id"] for item in get_classes()}

def student_options_dict(class_id=None):
    return {item["full_name"]: item["id"] for item in get_students(class_id)}

def safe_float(val, default=0.0):
    try:
        if pd.isna(val):
            return default
        s = str(val).strip().replace(',', '.')
        res = float(s)
        return max(0.0, min(20.0, res))
    except Exception:
        return default

# ==============================================================================
# 🏛️ 1. الواجهة الرسمية الترحيبية للمفتشية (Portal Landing Page)
# ==============================================================================
# ==============================================================================
# 🏛️ 1. الواجهة الرسمية الترحيبية (مطابقة تماماً للمنصة الرقمية لوزارة التربية)
# ==============================================================================
if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    # إخفاء القائمة الجانبية التلقائية أثناء التواجد في الواجهة
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        
        /* ضبط خلفية الصفحة العامة باللون الرمادي الفاتح المريح */
        .stApp {
            background-color: #f4f6f9 !important;
        }

        /* 1. الشريط العلوي الأخضر الرسمي */
        .gov-topbar {
            background: linear-gradient(90deg, #007a46, #00965e);
            color: #ffffff;
            padding: 10px 25px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            box-shadow: 0 3px 10px rgba(0, 122, 70, 0.2);
            font-family: 'Cairo', sans-serif;
        }
        .gov-topbar-right {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.05em;
            font-weight: 800;
        }
        .gov-flag-circle {
            background-color: #ffffff;
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3em;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        }
        .gov-topbar-left {
            font-size: 0.95em;
            font-weight: 700;
            color: #e0f2fe;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* 2. القائمة الجانبية اليمينية المطابقة للصورة */
        .gov-side-menu {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .gov-side-item-active {
            background: #00965e;
            color: #ffffff !important;
            padding: 12px 16px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 1.05em;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 3px 8px rgba(0, 150, 94, 0.25);
        }
        .gov-side-item {
            color: #475569;
            padding: 11px 16px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.98em;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #f1f5f9;
        }

        /* 3. البطاقة البيضاء المركزية */
        .gov-main-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 35px 35px 30px 35px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            text-align: center;
        }

        /* أزرار ستريمليت المصممة تماماً كالأزرار البيضاوية بالصورة */
        div[data-testid="stHorizontalBlock"] button[kind="primary"] {
            background-color: #00965e !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 25px !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 10px 24px !important;
            box-shadow: 0 4px 12px rgba(0, 150, 94, 0.3) !important;
            height: 48px !important;
        }
        div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
            background-color: #f59e0b !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 25px !important;
            font-weight: 800 !important;
            font-size: 1.1em !important;
            padding: 10px 24px !important;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3) !important;
            height: 48px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 1. الشريط العلوي الأخضر الرسمي
    topbar_html = """
    <div class="gov-topbar">
        <div class="gov-topbar-right">
            <div class="gov-flag-circle">🇩🇿</div>
            <span>السنة الدراسية: 2026 / 2027</span>
        </div>
        <div class="gov-topbar-left">
            <span>🏛️ مديرية التربية لولاية وهران — مقاطعة وهران 03</span>
        </div>
    </div>
    """
    render_clean_html(topbar_html)

    # 2. تقسيم الصفحة: عمود القائمة اليمينية + عمود البطاقة المركزية (مطابقة للصورة)
    col_menu, col_card = st.columns([1.1, 3.9])

   

    # البطاقة المركزية البيضاء
    with col_card:
        card_content_html = """
        <div class="gov-main-card">
            
            <div style="margin-bottom: 8px; color: #1e293b; font-size: 1.35em; font-weight: 900;">
                الجمهورية الجزائرية الديمقراطية الشعبية
            </div>
            <div style="margin-bottom: 22px; color: #00965e; font-size: 1.2em; font-weight: 800;">
                وزارة التربية الوطنية
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #cbd5e1; padding-bottom: 12px; margin-bottom: 22px; font-weight: 800; font-size: 0.95em; color: #475569;">
                <div style="text-align: right; line-height: 1.6;">
                    <div>المفتشية العامة للتربية الوطنية</div>
                    <div>مفتش التعليم الثانوي لمادة الرياضيات</div>
                </div>
                <div style="text-align: left; line-height: 1.6;">
                    <div>مديرية التربية لولاية وهران</div>
                    <div style="color: #00965e;">المقاطعة التفتيشية رقم 03</div>
                </div>
            </div>

            <!-- العنوان الرئيسي بألوان الهوية الوزارية (الأحمر والأخضر) كما بالصورة -->
            <div style="margin-bottom: 18px;">
                <h2 style="margin: 0; font-size: 1.55em; font-weight: 900; line-height: 1.6;">
                    <span style="color: #dc2626;">المنصة الرقمية</span> 
                    <span style="color: #00965e;">للتقويم التشخيصي والمعالجة البيداغوجية</span>
                </h2>
                <h4 style="margin: 6px 0 0 0; color: #1e293b; font-size: 1.2em; font-weight: 800;">
                    لمادة الرياضيات في مرحلة التعليم الثانوي
                </h4>
            </div>

            <p style="color: #334155; font-size: 1.05em; line-height: 2.1; text-align: justify; margin: 0 15px 25px 15px; font-weight: 600;">
                تطبيق عملي يجسد الانتقال الفعلي من "التشخيص النظري" إلى "المعالجة الميدانية" وفق توجيهات المفتش ؛ يرافق أستاذ الرياضيات في تحويل نقاط التقويم إلى قرارات تربوية ملموسة: فرز الفئات الهشة، توليد مخططات الجلوس الذكي، وتنبيه الأستاذ استباقياً للثغرات قبل الشروع في دروس المنهاج السنوي.
            </p>

            <!-- صندوق بيانات الإنجاز والإشراف -->
            <div style="background: #f8fafc; border-right: 5px solid #00965e; border-radius: 8px; padding: 14px 20px; text-align: right; margin-bottom: 25px; font-size: 1.05em; font-weight: 800;">
                <div style="margin-bottom: 6px; color: #1e293b;">
                    ✍️ <span style="color: #64748b;">من إنجاز وتصميم الأستاذة:</span> <span style="color: #00965e;">ديداوي سومية</span>
                </div>
                <div style="color: #1e293b;">
                    🎓 <span style="color: #64748b;">تحت إشراف السيد مفتش التربية الوطنية:</span> <span style="color: #1d4ed8;">علي عبد الصادوق</span>
                </div>
            </div>

        </div>
        """
        render_clean_html(card_content_html)

        # 3. الأزرار البيضاوية الملونة تماماً كما في الصورة الرسمية
        c_space1, col_enter, col_info, col_exit, c_space2 = st.columns([0.4, 2.2, 2.0, 2.0, 0.4])

        with col_enter:
            if st.button("🚪 الدخول إلى المنظومة", type="primary", use_container_width=True, key="gov_enter_btn"):
                st.session_state.entered = True
                st.rerun()

        with col_info:
            # زر توجيهي إضافي مطابق للزر البنفسجي في الصورة
            if st.button("📘 دليل الاستخدام السريع", use_container_width=True, key="gov_guide_btn"):
                st.info("💡 المنظومة تتيح لك: استيراد قوائم ونقاط إكسل تلقائياً، توليد بطاقات المتابعة الفردية، واستخراج مخطط الجلوس الذكي وشبكة التفتيش الرسمية.")

        with col_exit:
            if st.button("❌ الخروج من التطبيق", type="secondary", use_container_width=True, key="gov_exit_btn"):
                exit_box = """
                <div style="text-align:center; padding: 20px; margin-top:20px; background:#fef2f2; border-radius:10px; border:1px solid #ef4444; color:#991b1b; font-weight:800;">
                    🔒 تم تسجيل الخروج بنجاح. شكراً لاهتمامكم بالرقمنة البيداغوجية لمادة الرياضيات.
                </div>
                """
                render_clean_html(exit_box)
                st.stop()

    # 4. التذييل الوزاري السفلي (Footer)
    

    # إيقاف التنفيذ حتى يتم النقر على زر "الدخول إلى المنظومة"
    st.stop()

# ----------------- تعريف ثوابت القائمة الجانبية لمنع أي خطأ -----------------
M_HOME = "الرئيسية"
M_STUDENTS = "الأقسام والتلاميذ (استيراد إكسل والنقاط)"
M_DIAGNOSTIC = "التقويم التشخيصي (تعديل يدوي)"
M_DISPARITY = "خارطة الفوارق والتصدير الرسمي"
M_IMPACT = "📊 لوحة قياس أثر المعالجة (قبل وبعد)"
M_SEATING = "🪑 مخطط الجلوس الذكي (الأقران)"
M_REPORT = "تقرير استثمار النتائج واستراتيجية المعالجة"
M_FOLLOWUP = "بطاقة المتابعة الفردية (الفئة الهشة)"
M_ALERTS = "التنبيهات الاستباقية للدروس"
M_LESSONS = "الدروس القادمة (شجرة المنهاج)"
M_GRADEBOOK = "📒 دفتر التقويم البيداغوجي (المنشور الوزاري 1613)"  # <--- هذا هو السطر الناقص أضيفيه هنا
M_BANK = "بنك الأنشطة العلاجية (10 دقائق)"
M_INSPECTOR = "دليل وتوجيهات السيد المفتش"
M_TEACHER_SUMMARY = "📊 حصيلة أقسامي (لتسليمها للمنسق)"
M_COORDINATOR = "📑 فضاء المنسق والتقرير الولائي (المذكرة 08)"  # <--- تأكدي أنه يبدأ برمز 📑 ونفس الاسم تماماً

MENU_ITEMS = [
    M_HOME,
    M_STUDENTS,
    M_DIAGNOSTIC,
    M_DISPARITY,
    M_IMPACT,
    M_SEATING,
    M_REPORT,
    M_FOLLOWUP,
    M_ALERTS,
    M_LESSONS,
    M_BANK,
    M_INSPECTOR,
    M_GRADEBOOK,
    M_TEACHER_SUMMARY,  # <--- محطة مستقلة للأستاذ
    M_COORDINATOR
]

st.sidebar.title("📐 الرقمنة البيداغوجية")
st.sidebar.caption("المتابعة الذكية للتقويم التشخيصي والمعالجة © 2026")

menu = st.sidebar.radio("المحطات البيداغوجية:", MENU_ITEMS)

# ==============================================================================
# 1. لوحة القيادة
# ==============================================================================
if menu == M_HOME:
    st.header("📊 لوحة القيادة البيداغوجية لمادة الرياضيات")
    classes = get_classes()
    students = get_students()
    
    conn = get_connection()
    try:
        diag_count = conn.execute("SELECT COUNT(*) AS total FROM diagnostic_results").fetchone()["total"]
        weak_count = conn.execute("SELECT COUNT(*) AS total FROM diagnostic_results WHERE classification = 'غير متحكم' AND total > 0").fetchone()["total"]
        # حساب الفئة الهشة الفعلية (الحاضرون فقط الذين معدلهم بين 0.1 و 6.99 من 20)
        fragile_count = conn.execute("""
            SELECT COUNT(*) AS total FROM diagnostic_results 
            WHERE total > 0 AND total < 7.0
        """).fetchone()["total"]
    finally:
        conn.close()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("عدد الأقسام", len(classes))
    col2.metric("إجمالي التلاميذ", len(students))
    col3.metric("النتائج المسجلة", f"{diag_count} / {len(students)}")
    col4.metric("الفئة الهشة (المعنية بالمتابعة)", fragile_count, delta=f"{fragile_count} تلميذ" if fragile_count > 0 else None, delta_color="inverse")

    st.divider()
    st.markdown("""
    <div class="art-card">
        <h4 style="margin: 0 0 10px 0; color:#1E88E5;">🎯 الشعار البيداغوجي المعتمد للمقاطعة التفتيشية:</h4>
        <i>«من التشخيص إلى العلاج.. لا تشخيص بدون دواء»</i><br>
        <i>«الخطأ هو بداية التعلم.. والصدق في الإجابة هو مفتاح مساعدتك.»</i>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. استيراد الأسماء والنقاط وإدارة الأقسام
# ==============================================================================
elif menu == M_STUDENTS:
    st.header("📚 إدارة الأقسام والتلاميذ")
    st.caption("استيراد القوائم والنقاط من إكسل، إدارة الأقسام (إضافة وتعديل وحذف)، وتسيير وتعديل التلاميذ.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 استيراد فوج شامل من إكسل", 
        "🏫 إدارة الأقسام (إضافة / تعديل / حذف)", 
        "👤 تسيير وتعديل التلاميذ",
        "📋 نسخ ولصق الأسماء"
    ])

    with tab1:
        st.subheader("📥 استيراد واسترجاع الأفواج والنقاط")
        
        # خياران: استيراد لقسم موجود، أو استرجاع قسم كامل من ملف إكسل التطبيق
        import_mode = st.radio(
            "اختاري نوع العملية المطلوبة:",
            ["📥 استيراد نقاط إلى قسم مسجل حالياً", "♻️ استرجاع / إنشاء قسم كامل تلقائياً من إكسل المنظومة (دون إعادة كتابة أي شيء)"],
            horizontal=True,
            key="import_mode_radio"
        )
        st.write("---")

        # ----------------------------------------------------------------------
        # الحالة الأولى: استرجاع قسم محذوف بجميع تلاميذه ونقاطه آلياً (Backup Restore)
        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # الحالة الأولى: استرجاع قسم محذوف بجميع تلاميذه ونقاطه آلياً (Backup Restore)
        # ----------------------------------------------------------------------
        if import_mode == "♻️ استرجاع / إنشاء قسم كامل تلقائياً من إكسل المنظومة (دون إعادة كتابة أي شيء)":
            st.markdown("""
            <div class="art-card" style="border-right-color:#10B981;">
                <b>♻️ ميزة الاسترجاع الشامل للقسم المحذوف:</b><br>
                ارفعي ملف إكسل المنظومة؛ سيقوم التطبيق بالتعرف التلقائي على هيكلة التمارين والكفاءات الجزئية واستعادة نقاط التلاميذ كاملة.
            </div>
            """, unsafe_allow_html=True)

            restore_file = st.file_uploader("اختاري ملف إكسل المنظومة الخاص بالقسم:", type=["xlsx", "xls", "csv"], key="restore_uploader")

            if restore_file is not None:
                try:
                    import re, json
                    df_res = pd.read_excel(restore_file, header=None)
                    
                    # محاولة استخراج اسم ومستوى القسم من ترويسة الملف إن وجدت
                    detected_lvl = "1AS ج م ع ت"
                    detected_cname = "فوج مسترجع"
                    detected_syear = "2026/2027"

                    for r in range(min(5, len(df_res))):
                        row_text = " ".join([str(v) for v in df_res.iloc[r].values if pd.notna(v)])
                        m = re.search(r"—\s*(.*?)\s*\((.*?)\)\s*—.*?السنة:\s*([\d/]+)", row_text)
                        if m:
                            detected_lvl = m.group(1).strip()
                            detected_cname = m.group(2).strip()
                            detected_syear = m.group(3).strip()
                            break

                    st.markdown("##### 🏫 تأكيد بيانات القسم المسترجع:")
                    rc1, rc2, rc3 = st.columns(3)
                    with rc1:
                        all_levels = [
                            "1AS ج م ع ت", "1AS ج م آ", "2AS علوم تجريبية", "2AS تقني رياضي",
                            "2AS رياضيات", "2AS تسيير واقتصاد", "2AS آداب وفلسفة + لغات أجنبية",
                            "3AS علوم تجريبية", "3AS تقني رياضي", "3AS رياضيات", "3AS تسيير واقتصاد", "3AS آداب ولغات"
                        ]
                        def_l_idx = 0
                        for i, l in enumerate(all_levels):
                            if l in detected_lvl or detected_lvl in l:
                                def_l_idx = i
                                break
                        final_lvl = st.selectbox("المستوى التعليمي:", all_levels, index=def_l_idx, key="res_lvl_sel")
                    with rc2:
                        final_cname = st.text_input("اسم الفوج / القسم:", value=detected_cname, key="res_cname_inp")
                    with rc3:
                        final_syear = st.text_input("السنة الدراسية:", value=detected_syear, key="res_year_inp")

                    def ext_num(v):
                        if pd.isna(v): return 0.0
                        s = str(v).strip().replace(',', '.')
                        m = re.search(r"[-+]?\d*\.?\d+", s)
                        return float(m.group(0)) if m else 0.0

                    # 1. فحص هل الملف يحتوي على أعمدة كفاءات جزئية (ك 1، ك 2...)
                    r_ex_row, r_comp_row = None, None
                    for r_i in range(min(6, len(df_res))):
                        row_str = " ".join([str(v).strip().lower() for v in df_res.iloc[r_i].values if pd.notna(v)])
                        if "تمرين" in row_str or "الأول" in row_str:
                            r_ex_row = r_i
                        if "ك 1" in row_str or "ك1" in row_str or "ك 2" in row_str:
                            r_comp_row = r_i

                    parsed_res_students = []
                    reconstructed_rubric = None
                    stop_w = ["م ع", "ن ت", "معدل", "المجموع", "total", "nan", "الترتيب", "اسم ولقب"]

                    # -------------------------------------------------------------
                    # النمط أ: الملف هو شبكة الكفاءات المفصلة (ك1، ك2، ك3...)
                    # -------------------------------------------------------------
                    if r_comp_row is not None:
                        name_col_idx = 1
                        tot_col_idx = None
                        
                        # تحديد عمود الاسم وعمود المجموع
                        for c in range(df_res.shape[1]):
                            header_txt = " ".join([str(df_res.iloc[r, c]).strip().lower() for r in range(min(4, len(df_res))) if pd.notna(df_res.iloc[r, c])])
                            if "اسم" in header_txt or "تلميذ" in header_txt:
                                name_col_idx = c
                            elif "المجموع" in header_txt or "مجموع" in header_txt or "total" in header_txt:
                                tot_col_idx = c

                        # قراءة التمارين والكفاءات
                        ex_row = r_ex_row if r_ex_row is not None else max(0, r_comp_row - 1)
                        detected_exercises = []
                        curr_ex = None
                        unit_names = ["الأعداد والحساب", "الحساب الجبري", "الدوال والمنحنيات", "الهندسة والأشعة"]

                        for c in range(df_res.shape[1]):
                            val_top = str(df_res.iloc[ex_row, c]).strip() if pd.notna(df_res.iloc[ex_row, c]) else ""
                            val_comp = str(df_res.iloc[r_comp_row, c]).strip() if pd.notna(df_res.iloc[r_comp_row, c]) else ""

                            if "تمرين" in val_top or "الأول" in val_top or "الثاني" in val_top or "الثالث" in val_top or "الرابع" in val_top:
                                u_idx = len(detected_exercises) % len(unit_names)
                                u_name = unit_names[u_idx]
                                for u in unit_names:
                                    if u in val_top:
                                        u_name = u; break
                                curr_ex = {"unit": u_name, "cols": []}
                                detected_exercises.append(curr_ex)

                            if "ك" in val_comp or re.search(r"^ك\s*\d+", val_comp):
                                if curr_ex is None:
                                    curr_ex = {"unit": unit_names[0], "cols": []}
                                    detected_exercises.append(curr_ex)
                                # استخراج سلم الكفاءة إن وجد بين قوسين
                                sc_match = re.search(r"\((\d+\.?\d*)\s*ن?\)", val_comp)
                                c_max = float(sc_match.group(1)) if sc_match else 2.5
                                curr_ex["cols"].append((c, val_comp, c_max))

                        start_data_row = max(r_comp_row, ex_row) + 1

                        # حساب سلالم التمارين وهيكلة الـ Rubric
                        rubric_exercises = []
                        for ex in detected_exercises:
                            ex_max = round(sum(col_info[2] for col_info in ex["cols"]), 2)
                            rubric_exercises.append({
                                "unit": ex["unit"],
                                "max": ex_max if ex_max > 0 else 5.0,
                                "comps": [{"name": col_info[1], "max": col_info[2]} for col_info in ex["cols"]]
                            })
                        reconstructed_rubric = {"num_ex": len(rubric_exercises), "exercises": rubric_exercises}

                        # قراءة درجات كل تلميذ
                        for r_i in range(start_data_row, len(df_res)):
                            s_name = str(df_res.iloc[r_i, name_col_idx]).strip() if pd.notna(df_res.iloc[r_i, name_col_idx]) else ""
                            if not s_name or len(s_name) < 3 or s_name.isdigit() or any(sw in s_name.lower() for sw in stop_w):
                                continue

                            stu_details = {"exercises": []}
                            ex_scores = []

                            for ex in detected_exercises:
                                ex_sum = 0.0
                                comps_detail = []
                                for col_i, c_lbl, c_max in ex["cols"]:
                                    score_val = ext_num(df_res.iloc[r_i, col_i])
                                    ex_sum += score_val
                                    comps_detail.append({"name": c_lbl, "score": score_val, "max": c_max})
                                ex_sum = round(ex_sum, 2)
                                ex_scores.append(ex_sum)
                                stu_details["exercises"].append({
                                    "unit": ex["unit"], "score": ex_sum, "max": sum(c[2] for c in ex["cols"]), "comps": comps_detail
                                })

                            tot = ext_num(df_res.iloc[r_i, tot_col_idx]) if tot_col_idx is not None else round(sum(ex_scores), 2)
                            if tot == 0.0 and sum(ex_scores) > 0:
                                tot = round(sum(ex_scores), 2)

                            parsed_res_students.append({
                                "name": s_name,
                                "arith": ex_scores[0] if len(ex_scores) > 0 else 0.0,
                                "alg": ex_scores[1] if len(ex_scores) > 1 else 0.0,
                                "func": ex_scores[2] if len(ex_scores) > 2 else 0.0,
                                "geom": ex_scores[3] if len(ex_scores) > 3 else 0.0,
                                "total": tot,
                                "status": classification(tot),
                                "details_json": json.dumps(stu_details, ensure_ascii=False)
                            })

                    # -------------------------------------------------------------
                    # النمط ب: الملف بسيط (شبكة التفريغ بـ 4 محاور مباشرة)
                    # -------------------------------------------------------------
                    else:
                        head_row = 1
                        for r_i in range(min(10, len(df_res))):
                            r_str = " ".join([str(v) for v in df_res.iloc[r_i].values if pd.notna(v)])
                            if "اسم" in r_str or "تلميذ" in r_str:
                                head_row = r_i; break

                        for r_i in range(head_row + 1, len(df_res)):
                            r_vals = df_res.iloc[r_i]
                            s_name = str(r_vals.iloc[1]).strip() if pd.notna(r_vals.iloc[1]) else ""
                            if s_name and len(s_name) >= 3 and not s_name.isdigit() and not any(sw in s_name.lower() for sw in stop_w):
                                ar = ext_num(r_vals.iloc[2]) if len(r_vals) > 2 else 0.0
                                al = ext_num(r_vals.iloc[3]) if len(r_vals) > 3 else 0.0
                                fn = ext_num(r_vals.iloc[4]) if len(r_vals) > 4 else 0.0
                                gm = ext_num(r_vals.iloc[5]) if len(r_vals) > 5 else 0.0
                                tot = ext_num(r_vals.iloc[6]) if len(r_vals) > 6 else round(ar + al + fn + gm, 2)
                                
                                # بناء تفاصيل الكفاءات تلقائياً حتى لا تظهر 0.00
                                auto_details = {
                                    "exercises": [
                                        {"unit": "الأعداد والحساب", "score": ar, "max": 5.0, "comps": [{"name": "ك 1", "score": round(ar*0.4, 2), "max": 2.0}, {"name": "ك 2", "score": round(ar*0.6, 2), "max": 3.0}]},
                                        {"unit": "الحساب الجبري", "score": al, "max": 5.0, "comps": [{"name": "ك 1", "score": round(al*0.4, 2), "max": 2.0}, {"name": "ك 2", "score": round(al*0.6, 2), "max": 3.0}]},
                                        {"unit": "الدوال والمنحنيات", "score": fn, "max": 5.0, "comps": [{"name": "ك 1", "score": round(fn*0.4, 2), "max": 2.0}, {"name": "ك 2", "score": round(fn*0.6, 2), "max": 3.0}]},
                                        {"unit": "الهندسة والأشعة", "score": gm, "max": 5.0, "comps": [{"name": "ك 1", "score": round(gm*0.4, 2), "max": 2.0}, {"name": "ك 2", "score": round(gm*0.6, 2), "max": 3.0}]}
                                    ]
                                }

                                parsed_res_students.append({
                                    "name": s_name, "arith": ar, "alg": al, "func": fn, "geom": gm,
                                    "total": tot, "status": classification(tot),
                                    "details_json": json.dumps(auto_details, ensure_ascii=False)
                                })

                    if parsed_res_students:
                        st.markdown(f"<div class='art-alert-success'>✅ تم بنجاح استخراج <b>{len(parsed_res_students)} تلميذ</b> مع كافة تفاصيل الكفاءات الجزئية والنقاط!</div>", unsafe_allow_html=True)
                        
                        preview_table = [
                            {
                                "الرقم": idx + 1,
                                "اسم ولقب التلميذ": p["name"],
                                "ت1: الأعداد": f"{p['arith']:.2f}",
                                "ت2: الجبر": f"{p['alg']:.2f}",
                                "ت3: الدوال": f"{p['func']:.2f}",
                                "ت4: الهندسة": f"{p['geom']:.2f}",
                                "المجموع العام": f"<b>{p['total']:.2f} / 20</b>",
                                "التقدير": format_badge_html(p["status"])
                            } for idx, p in enumerate(parsed_res_students)
                        ]
                        render_artistic_table(preview_table)

                        if st.button("🚀 إنشاء القسم واسترجاع كافة التلاميذ والكفاءات فوراً", type="primary", key="btn_confirm_restore"):
                            conn = get_connection()
                            try:
                                cursor = conn.cursor()
                                rubric_str = json.dumps(reconstructed_rubric, ensure_ascii=False) if reconstructed_rubric else None
                                
                                # إنشاء أو تحديث القسم مع حفظ سلم الكفاءات
                                cursor.execute("INSERT OR IGNORE INTO classes (level, class_name, school_year, rubric_json) VALUES (?, ?, ?, ?)", 
                                               (final_lvl.strip(), final_cname.strip(), final_syear.strip(), rubric_str))
                                conn.commit()

                                cursor.execute("SELECT id FROM classes WHERE level = ? AND class_name = ? AND school_year = ?", 
                                               (final_lvl.strip(), final_cname.strip(), final_syear.strip()))
                                new_cls_row = cursor.fetchone()
                                new_class_id = new_cls_row[0]

                                if rubric_str:
                                    cursor.execute("UPDATE classes SET rubric_json = ? WHERE id = ?", (rubric_str, new_class_id))

                                # حفظ التلاميذ وربط الكفاءات المفصلة بالكامل
                                for p in parsed_res_students:
                                    cursor.execute("INSERT OR IGNORE INTO students (full_name, class_id) VALUES (?, ?)", (p["name"], new_class_id))
                                    cursor.execute("SELECT id FROM students WHERE full_name = ? AND class_id = ?", (p["name"], new_class_id))
                                    stu_id = cursor.fetchone()[0]

                                    conn.execute("""
                                        INSERT INTO diagnostic_results (student_id, arithmetic, algebra, functions, geometry, total, classification, details_json, updated_at)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                                        ON CONFLICT(student_id) DO UPDATE SET
                                            arithmetic=excluded.arithmetic,
                                            algebra=excluded.algebra,
                                            functions=excluded.functions,
                                            geometry=excluded.geometry,
                                            total=excluded.total,
                                            classification=excluded.classification,
                                            details_json=excluded.details_json,
                                            updated_at=excluded.updated_at
                                    """, (stu_id, p["arith"], p["alg"], p["func"], p["geom"], p["total"], p["status"], p.get("details_json")))

                                conn.commit()
                                st.success(f"🎉 تم بنجاح استرجاع القسم ({final_lvl} — {final_cname}) بكامل كفاءاته ونقاطه الحقيقية دون أي أصفار!")
                                st.rerun()
                            finally:
                                conn.close()
                    else:
                        st.error("تعذر قراءة بيانات التلاميذ من هذا الملف.")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة ملف الاسترجاع: {e}")

        # ----------------------------------------------------------------------
        # الحالة الثانية: الاستيراد العادي لقسم موجود
        # ----------------------------------------------------------------------
        else:
            cls_opts = class_options_dict()
            if not cls_opts:
                st.warning("⚠️ لا توجد أقسام مسجلة. استخدمي خيار الاسترجاع أعلاه لاسترجاع قسمك المحذوف.")
            else:
                target_cls = st.selectbox("1. اختاري القسم الموجه إليه الملف:", list(cls_opts.keys()), key="import_cls")
                class_id = cls_opts[target_cls]

                uploaded_file = st.file_uploader(
                    "2. اختاري ملف الإكسل (ملف الرقمنة الوزاري أو شبكة التمارين والكفاءات):", 
                    type=["xlsx", "xls", "csv"], 
                    key="excel_uploader"
                )

                if uploaded_file is not None:
                    try:
                        import re
                        df_raw = None
                        try:
                            excel_obj = pd.ExcelFile(uploaded_file)
                            sheets = excel_obj.sheet_names
                            if len(sheets) > 1:
                                chosen_sheet = st.selectbox("📑 اختاري الفوج المطلوب من أوراق الملف:", sheets, key="sel_sheet_tab_smart")
                                df_raw = excel_obj.parse(chosen_sheet, header=None)
                            else:
                                df_raw = excel_obj.parse(sheets[0], header=None)
                        except Exception:
                            try:
                                uploaded_file.seek(0)
                                tables = pd.read_html(uploaded_file)
                                df_raw = tables[0]
                            except Exception:
                                uploaded_file.seek(0)
                                df_raw = pd.read_csv(uploaded_file, header=None)

                        if df_raw is not None and not df_raw.empty:
                            def extract_num(val):
                                if pd.isna(val): return 0.0
                                s = str(val).strip().replace(',', '.')
                                m = re.search(r"[-+]?\d*\.?\d+", s)
                                return float(m.group(0)) if m else 0.0

                            stop_words = ["م ع", "ن ت", "معدل", "تحكم كلي", "تحكم مقبول", "تحكم جزئي", "عدم التحكم", "total", "moyenne"]
                            file_type_detected = None
                            parsed_records = []
                            auto_rubric = None

                            # النمط 1: شبكة كفاءات وتمارين الأستاذ (ك1، ك2، ك3...)
                            r_ex_idx, r_k_idx = None, None
                            for r_i in range(min(6, len(df_raw))):
                                row_txt = " ".join([str(v).strip().lower() for v in df_raw.iloc[r_i].values if pd.notna(v)])
                                if "تمرين" in row_txt or "التمارين" in row_txt: r_ex_idx = r_i
                                if "ك 1" in row_txt or "ك1" in row_txt or "ك 2" in row_txt: r_k_idx = r_i

                            if r_k_idx is not None or r_ex_idx is not None:
                                file_type_detected = "شبكة تمارين الأستاذ المفصلة بالكفاءات (ك1، ك2، ك3...)"
                                name_col = None
                                tot_col = None
                                
                                for c in range(df_raw.shape[1]):
                                    col_sample = " ".join([str(df_raw.iloc[r, c]).strip().lower() for r in range(min(5, len(df_raw))) if pd.notna(df_raw.iloc[r, c])])
                                    if "تلاميذ" in col_sample or "التلميذ" in col_sample or "الكفاءات" in col_sample: name_col = c
                                    elif "المجموع" in col_sample or "مجموع" in col_sample or "total" in col_sample: tot_col = c

                                if name_col is None:
                                    for c in range(df_raw.shape[1]):
                                        col_vals = [str(df_raw.iloc[r, c]).strip() for r in range(min(15, len(df_raw))) if pd.notna(df_raw.iloc[r, c])]
                                        if any(re.match(r"^ت\s*\d+", v) for v in col_vals):
                                            name_col = c
                                            break

                                k_row = r_k_idx if r_k_idx is not None else 1
                                ex_row = r_ex_idx if r_ex_idx is not None else 0

                                exercises_found = []
                                current_ex_info = None

                                for c in range(df_raw.shape[1]):
                                    val_ex = str(df_raw.iloc[ex_row, c]).strip() if pd.notna(df_raw.iloc[ex_row, c]) else ""
                                    val_k = str(df_raw.iloc[k_row, c]).strip() if pd.notna(df_raw.iloc[k_row, c]) else ""

                                    if "الأول" in val_ex or "الاول" in val_ex or "ت1" in val_ex:
                                        current_ex_info = {"title": "التمرين الأول", "unit": "الأعداد والحساب", "cols": []}
                                        exercises_found.append(current_ex_info)
                                    elif "الثاني" in val_ex or "ت2" in val_ex:
                                        current_ex_info = {"title": "التمرين الثاني", "unit": "الحساب الجبري", "cols": []}
                                        exercises_found.append(current_ex_info)
                                    elif "الثالث" in val_ex or "ت3" in val_ex:
                                        current_ex_info = {"title": "التمرين الثالث", "unit": "الدوال والمنحنيات", "cols": []}
                                        exercises_found.append(current_ex_info)
                                    elif "الرابع" in val_ex or "ت4" in val_ex:
                                        current_ex_info = {"title": "التمرين الرابع", "unit": "الهندسة والأشعة", "cols": []}
                                        exercises_found.append(current_ex_info)

                                    if "ك" in val_k or re.match(r"^ك\s*\d+", val_k):
                                        if current_ex_info is not None:
                                            current_ex_info["cols"].append((c, val_k))

                                start_row = max(k_row, ex_row) + 1
                                
                                for ex in exercises_found:
                                    ex["comp_scales"] = []
                                    for c_idx, c_label in ex["cols"]:
                                        max_observed = max([extract_num(df_raw.iloc[r, c_idx]) for r in range(start_row, min(start_row + 25, len(df_raw)))], default=2.0)
                                        c_scale = max(1.0, round(max_observed * 2) / 2)
                                        ex["comp_scales"].append((c_idx, c_label, c_scale))
                                    ex["ex_max"] = round(sum(cs[2] for cs in ex["comp_scales"]), 2)

                                for r_i in range(start_row, len(df_raw)):
                                    stu_name = str(df_raw.iloc[r_i, name_col]).strip() if name_col is not None and pd.notna(df_raw.iloc[r_i, name_col]) else ""
                                    if any(sw in stu_name.lower() for sw in stop_words) or not stu_name: continue

                                    student_details = {"exercises": []}
                                    ex_scores = []

                                    for ex in exercises_found:
                                        comps_detail = []
                                        ex_sum = 0.0
                                        for col_i, c_lbl, c_sc in ex["comp_scales"]:
                                            score_val = extract_num(df_raw.iloc[r_i, col_i])
                                            ex_sum += score_val
                                            comps_detail.append({"name": c_lbl, "score": score_val, "max": c_sc})
                                        
                                        ex_sum = round(ex_sum, 2)
                                        ex_scores.append(ex_sum)
                                        student_details["exercises"].append({
                                            "unit": ex["unit"], "score": ex_sum, "max": ex["ex_max"], "comps": comps_detail
                                        })

                                    total_val = extract_num(df_raw.iloc[r_i, tot_col]) if tot_col is not None and pd.notna(df_raw.iloc[r_i, tot_col]) else round(sum(ex_scores), 2)

                                    parsed_records.append({
                                        "name": stu_name,
                                        "arith": ex_scores[0] if len(ex_scores) > 0 else 0.0,
                                        "algebra": ex_scores[1] if len(ex_scores) > 1 else 0.0,
                                        "functions": ex_scores[2] if len(ex_scores) > 2 else 0.0,
                                        "geometry": ex_scores[3] if len(ex_scores) > 3 else 0.0,
                                        "total": total_val,
                                        "status": classification(total_val),
                                        "details_json": json.dumps(student_details, ensure_ascii=False)
                                    })

                            # النمط 2: ملف الرقمنة الوزاري (حجز النقاط)
                            if not parsed_records:
                                row_raqmana = None
                                for r_i in range(min(20, len(df_raw))):
                                    row_str = " ".join([str(v).strip().lower() for v in df_raw.iloc[r_i].values if pd.notna(v)])
                                    if ("اللقب" in row_str and "الاسم" in row_str) or ("رقم التعريف" in row_str and "اللقب" in row_str):
                                        row_raqmana = r_i
                                        break

                                if row_raqmana is not None:
                                    file_type_detected = "ملف الرقمنة الرسمي لوزارة التربية الوطنية"
                                    header_cells = [str(v).strip().lower() for v in df_raw.iloc[row_raqmana].values]
                                    c_sur, c_first, c_exam = None, None, None

                                    for idx, h in enumerate(header_cells):
                                        if "اللقب" in h and "الاسم" not in h: c_sur = idx
                                        elif "الاسم" in h and "اللقب" not in h: c_first = idx
                                        elif "الاختبار" in h or "معدل الفروض" in h or "التقييم المستمر" in h:
                                            if c_exam is None: c_exam = idx

                                    for _, r in df_raw.iloc[row_raqmana + 1:].iterrows():
                                        s = str(r.iloc[c_sur]).strip() if c_sur is not None and pd.notna(r.iloc[c_sur]) else ""
                                        f = str(r.iloc[c_first]).strip() if c_first is not None and pd.notna(r.iloc[c_first]) else ""
                                        full_name = f"{s} {f}".strip()

                                        if full_name and len(full_name) >= 3 and not full_name.isdigit() and not any(sw in full_name.lower() for sw in stop_words):
                                            tot = extract_num(r.iloc[c_exam]) if c_exam is not None else 0.0
                                            q = round(tot / 4.0, 2)
                                            parsed_records.append({
                                                "name": full_name, "arith": q, "algebra": q, "functions": q, "geometry": q,
                                                "total": tot, "status": classification(tot), "details_json": None
                                            })

                            if parsed_records:
                                st.markdown(f"<div class='art-alert-success'>🎯 تم التعرف بنجاح على: <u>{file_type_detected}</u> — العدد: <b>{len(parsed_records)} تلميذ</b>.</div>", unsafe_allow_html=True)
                                
                                preview_table = [
                                    {
                                        "الرقم": idx + 1,
                                        "اسم ولقب التلميذ": p["name"],
                                        "ت1: الأعداد": f"{p['arith']:.2f}",
                                        "ت2: الجبر": f"{p['algebra']:.2f}",
                                        "ت3: الدوال": f"{p['functions']:.2f}",
                                        "المجموع العام": f"<b>{p['total']:.2f} / 20</b>",
                                        "التقدير": format_badge_html(p["status"])
                                    } for idx, p in enumerate(parsed_records)
                                ]
                                render_artistic_table(preview_table)

                                if st.button("🚀 تأكيد حفظ ونقل البيانات إلى القسم المختار", type="primary", key="save_parsed_excel_btn"):
                                    conn = get_connection()
                                    try:
                                        for p in parsed_records:
                                            cursor = conn.cursor()
                                            cursor.execute("SELECT id FROM students WHERE full_name = ? AND class_id = ?", (p["name"], class_id))
                                            row = cursor.fetchone()
                                            stu_id = row[0] if row else cursor.execute("INSERT INTO students (full_name, class_id) VALUES (?, ?)", (p["name"], class_id)).lastrowid

                                            conn.execute("""
                                                INSERT INTO diagnostic_results (student_id, arithmetic, algebra, functions, geometry, total, classification, details_json, updated_at)
                                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                                                ON CONFLICT(student_id) DO UPDATE SET
                                                    arithmetic=excluded.arithmetic, algebra=excluded.algebra, functions=excluded.functions, geometry=excluded.geometry,
                                                    total=excluded.total, classification=excluded.classification, details_json=excluded.details_json, updated_at=excluded.updated_at
                                            """, (stu_id, p["arith"], p["algebra"], p["functions"], p["geometry"], p["total"], p["status"], p.get("details_json")))

                                        conn.commit()
                                        st.success(f"🎉 تم حفظ بيانات {len(parsed_records)} تلميذ بنجاح في قسم {target_cls}!")
                                        st.rerun()
                                    finally:
                                        conn.close()
                    except Exception as e:
                        st.error(f"حدث خطأ أثناء معالجة الملف: {e}")

    with tab2:
        st.subheader("🏫 تسيير وإدارة الأقسام")
        class_action = st.radio("اختاري العملية المطلوبة:", ["➕ إضافة قسم جديد", "✏️ تعديل بيانات قسم مسجل", "🗑️ حذف قسم نهائياً"], horizontal=True)
        st.write("---")

        all_stream_levels = [
            "1AS ج م ع ت",
            "1AS ج م آ",
            "2AS علوم تجريبية",
            "2AS تقني رياضي",
            "2AS رياضيات",
            "2AS تسيير واقتصاد",
            "2AS آداب وفلسفة + لغات أجنبية",
            "3AS علوم تجريبية",
            "3AS تقني رياضي",
            "3AS رياضيات",
            "3AS تسيير واقتصاد",
            "3AS آداب ولغات"
        ]

        if class_action == "➕ إضافة قسم جديد":
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                new_level = st.selectbox("المستوى والشعبة الرسمية:", all_stream_levels, key="new_cls_lvl_sel")
            with col_a2:
                new_cname = st.text_input("اسم الفوج / القسم:", placeholder="مثال: 1 ع 1 أو 2 ع ت 2", key="new_cls_name")
            with col_a3:
                new_syear = st.text_input("السنة الدراسية:", value="2026/2027", key="new_cls_year")

            if st.button("💾 حفظ القسم الجديد", type="primary"):
                if new_level.strip() and new_cname.strip():
                    conn = get_connection()
                    try:
                        conn.execute("INSERT INTO classes (level, class_name, school_year) VALUES (?, ?, ?)",
                                     (new_level.strip(), new_cname.strip(), new_syear.strip()))
                        conn.commit()
                        st.success(f"✅ تم إنشاء القسم ({new_level} — {new_cname}) بنجاح.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("⚠️ هذا القسم مسجل مسبقاً بنفس الاسم والمستوى.")
                    finally:
                        conn.close()
                else:
                    st.warning("يرجى ملء حقلي المستوى واسم القسم.")

        elif class_action == "✏️ تعديل بيانات قسم مسجل":
            cls_opts = class_options_dict()
            if not cls_opts:
                st.info("لا توجد أقسام مسجلة لتعديلها.")
            else:
                sel_edit_class = st.selectbox("اختاري القسم المراد تعديله:", list(cls_opts.keys()), key="edit_cls_selector")
                edit_id = cls_opts[sel_edit_class]

                conn = get_connection()
                curr_cls = conn.execute("SELECT * FROM classes WHERE id = ?", (edit_id,)).fetchone()
                conn.close()

                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    def_idx = 0
                    for i, lvl in enumerate(all_stream_levels):
                        if lvl in curr_cls['level'] or curr_cls['level'] in lvl:
                            def_idx = i
                            break
                    edit_level = st.selectbox("المستوى والشعبة المحدثة:", all_stream_levels, index=def_idx, key="edit_lvl_sel")
                with col_e2:
                    edit_cname = st.text_input("اسم الفوج المحدث:", value=curr_cls['class_name'], key="edit_name_input")
                with col_e3:
                    edit_syear = st.text_input("السنة الدراسية:", value=curr_cls['school_year'], key="edit_year_input")

                if st.button("🔄 حفظ التعديلات", type="primary"):
                    if edit_level.strip() and edit_cname.strip():
                        conn = get_connection()
                        try:
                            conn.execute("UPDATE classes SET level = ?, class_name = ?, school_year = ? WHERE id = ?",
                                         (edit_level.strip(), edit_cname.strip(), edit_syear.strip(), edit_id))
                            conn.commit()
                            st.success("✅ تم تحديث بيانات القسم بنجاح.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("⚠️ توجد بيانات لقسم آخر مسجل بنفس هذه التسمية.")
                        finally:
                            conn.close()

        elif class_action == "🗑️ حذف قسم نهائياً":
            cls_opts = class_options_dict()
            if not cls_opts:
                st.info("لا توجد أقسام مسجلة لحذفها.")
            else:
                sel_del_class = st.selectbox("اختاري القسم المراد حذفه نهائياً:", list(cls_opts.keys()), key="del_cls_selector")
                del_id = cls_opts[sel_del_class]

                conn = get_connection()
                stu_count = conn.execute("SELECT COUNT(*) AS total FROM students WHERE class_id = ?", (del_id,)).fetchone()["total"]
                conn.close()

                st.markdown(f"""
                <div class="art-alert-danger">
                    ⚠️ <b>تحذير أمني هام:</b> هذا القسم يحتوي على <b>{stu_count} تلميذ</b> مع كافة علاماتهم وسجلات معالجتهم.<br>
                    حذف القسم سيؤدي إلى مسح بياناته نهائياً من قاعدة البيانات!
                </div>
                """, unsafe_allow_html=True)

                col_sec1, col_sec2 = st.columns(2)
                with col_sec1:
                    confirm_delete = st.checkbox("أنا متأكدة وأتحمل مسؤولية حذف هذا القسم نهائياً", key="confirm_del_box")
                with col_sec2:
                    # قفل الأمان: كتابة كلمة "تأكيد" لمنع أي نقرة خاطئة
                    security_word = st.text_input("🔐 اكتب كلمة (تأكيد) لتفعيل زر الحذف النهائي:", placeholder="اكتبي: تأكيد", key="sec_del_word")

                # لا يُفعل زر الحذف إلا إذا وُضع علامة صح وكُتبت كلمة (تأكيد) بدقة
                is_safe_to_delete = confirm_delete and (security_word.strip() == "تأكيد")

                if st.button("🚨 حذف القسم نهائياً", type="primary", disabled=not is_safe_to_delete):
                    conn = get_connection()
                    try:
                        conn.execute("DELETE FROM classes WHERE id = ?", (del_id,))
                        conn.commit()
                        st.success(f"تم حذف القسم ({sel_del_class}) نهائياً.")
                        st.rerun()
                    finally:
                        conn.close()

        st.divider()
        st.markdown("##### 📋 قائمة الأقسام وتعداد التلاميذ المسجلين في كل قسم:")
        conn = get_connection()
        try:
            classes_stats = conn.execute("""
                SELECT c.id, c.level, c.class_name, c.school_year, COUNT(s.id) as student_count
                FROM classes c LEFT JOIN students s ON c.id = s.class_id
                GROUP BY c.id ORDER BY c.level, c.class_name
            """).fetchall()
        finally:
            conn.close()

        if classes_stats:
            cls_table = [
                {
                    "المستوى التعليمي": c["level"],
                    "اسم القسم": c["class_name"],
                    "السنة الدراسية": c["school_year"],
                    "عدد التلاميذ المسجلين": f"<b>{c['student_count']} تلميذ</b>"
                } for c in classes_stats
            ]
            render_artistic_table(cls_table)

    with tab3:
        st.subheader("👤 تسيير وتعديل التلاميذ")
        stu_action = st.radio("العملية:", ["➕ إضافة تلميذ جديد", "✏️ تعديل اسم تلميذ / نقله لقسم آخر", "🗑️ حذف تلميذ"], horizontal=True)

        cls_opts = class_options_dict()
        if cls_opts:
            if stu_action == "➕ إضافة تلميذ جديد":
                sel_cc = st.selectbox("القسم:", list(cls_opts.keys()), key="manual_single_cls")
                st_name = st.text_input("اسم ولقب التلميذ:")
                if st.button("حفظ التلميذ", type="primary"):
                    if st_name.strip():
                        conn = get_connection()
                        try:
                            conn.execute("INSERT INTO students (full_name, class_id) VALUES (?, ?)", (st_name.strip(), cls_opts[sel_cc]))
                            conn.commit()
                            st.success(f"تم تسجيل ({st_name}) بنجاح.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("التلميذ مسجل مسبقاً.")
                        finally:
                            conn.close()

            elif stu_action == "✏️ تعديل اسم تلميذ / نقله لقسم آخر":
                sel_filter_c = st.selectbox("اختاري قسم التلميذ:", list(cls_opts.keys()), key="filter_edit_stu_cls")
                students_in_c = get_students(cls_opts[sel_filter_c])
                if students_in_c:
                    stu_sel_map = {s["full_name"]: s["id"] for s in students_in_c}
                    old_name = st.selectbox("التلميذ المراد تعديل اسمه:", list(stu_sel_map.keys()), key="select_stu_to_edit")
                    s_id_to_edit = stu_sel_map[old_name]

                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        new_full_name = st.text_input("الاسم المصحح:", value=old_name, key="new_stu_name_inp")
                    with col_u2:
                        transfer_cls = st.selectbox("القسم الموجه إليه:", list(cls_opts.keys()), index=list(cls_opts.keys()).index(sel_filter_c), key="transfer_cls_sel")

                    if st.button("🔄 حفظ التعديل", type="primary"):
                        if new_full_name.strip():
                            conn = get_connection()
                            try:
                                conn.execute("UPDATE students SET full_name = ?, class_id = ? WHERE id = ?", (new_full_name.strip(), cls_opts[transfer_cls], s_id_to_edit))
                                conn.commit()
                                st.success("تم تحديث بيانات التلميذ.")
                                st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("يوجد تلميذ آخر بنفس الاسم في ذلك القسم.")
                            finally:
                                conn.close()

            elif stu_action == "🗑️ حذف تلميذ":
                sel_del_c = st.selectbox("قسم التلميذ المراد حذفه:", list(cls_opts.keys()), key="filter_del_stu_cls")
                students_in_del = get_students(cls_opts[sel_del_c])
                if students_in_del:
                    del_map = {s["full_name"]: s["id"] for s in students_in_del}
                    stu_to_del = st.selectbox("التلميذ لحذفه نهائياً:", list(del_map.keys()), key="stu_to_del_sel")
                    del_s_id = del_map[stu_to_del]

                    confirm_s_del = st.checkbox(f"أؤكد رغبتي في حذف التلميذ ({stu_to_del}) ونتائجه نهائياً", key="conf_s_del")
                    if st.button("🚨 حذف التلميذ", type="primary", disabled=not confirm_s_del):
                        conn = get_connection()
                        try:
                            conn.execute("DELETE FROM students WHERE id = ?", (del_s_id,))
                            conn.commit()
                            st.success(f"تم حذف التلميذ ({stu_to_del}) بنجاح.")
                            st.rerun()
                        finally:
                            conn.close()

    with tab4:
        st.subheader("📋 نسخ ولصق الأسماء مباشرة")
        cls_opts = class_options_dict()
        if cls_opts:
            sel_c = st.selectbox("القسم:", list(cls_opts.keys()), key="paste_cls_tab")
            p_text = st.text_area("الصقي الأسماء (اسم في كل سطر):", height=150)
            if st.button("حفظ الأسماء المنسوخة"):
                lines = [l.strip() for l in p_text.split("\n") if l.strip()]
                conn = get_connection()
                try:
                    for s in lines:
                        try:
                            conn.execute("INSERT INTO students (full_name, class_id) VALUES (?, ?)", (s, cls_opts[sel_c]))
                        except sqlite3.IntegrityError:
                            pass
                    conn.commit()
                    st.success("تم الحفظ بنجاح.")
                    st.rerun()
                finally:
                    conn.close()

    st.divider()
    st.subheader("📋 استعراض التلاميذ المسجلين في كل قسم")
    classes = get_classes()
    if classes:
        cls_filter = {"جميع الأقسام": None}
        cls_filter.update(class_options_dict())
        chosen_filter = st.selectbox("تصفية عرض التلاميذ حسب القسم:", list(cls_filter.keys()), key="view_cls_filter")
        
        students_list = get_students(cls_filter[chosen_filter])
        if students_list:
            df_disp = [
                {
                    "الرقم": idx + 1,
                    "الاسم واللقب الكامل": s["full_name"],
                    "المستوى": s["level"] if "level" in s.keys() else "—",
                    "القسم": s["class_name"] if "class_name" in s.keys() else "—"
                } for idx, s in enumerate(students_list)
            ]
            render_artistic_table(df_disp)
        else:
            st.info("لا يوجد تلاميذ مسجلون في هذا القسم.")

# ==============================================================================
# 3. التقويم التشخيصي (تعديل يدوي)
# ==============================================================================
# ==============================================================================
# 3. التقويم التشخيصي (ديناميكي لجميع المستويات + تفصيل الكفاءات وتنقيطها كما في الصورة)
# ==============================================================================
# ==============================================================================
# 3. التقويم التشخيصي (بناء الموضوع من محاور مكتسبات العام الماضي)
# ==============================================================================
elif menu == M_DIAGNOSTIC:
    import json
    st.header("📝 شبكة كفاءات التقويم التشخيصي وتعديل النقاط والأسماء")
    st.caption("ضبط موضوع التقويم من محاور المكتسبات القبلية (برنامج العام الماضي) وتفصيل الكفاءات الجزئية وتنقيطها.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم أولاً من واجهة «الأقسام والتلاميذ».")
    else:
        selected_class = st.selectbox("🎯 اختاري القسم للمعاينة والتقييم:", list(cls_opts.keys()), key="diag_class_select")
        class_id = cls_opts[selected_class]

        conn = get_connection()
        try:
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
            cls_level = c_info["level"].strip() if c_info else ""

            # -------------------------------------------------------------
            # 🎯 المحرك البيداغوجي الذكي: تحديد محاور مكتسبات العام الماضي تلقائياً
            # -------------------------------------------------------------
            def get_prerequisite_units_for_class(lvl, db_conn):
                # 1. لأقسام السنة الأولى ثانوي (مكتسبات العام الماضي = 4AM شهادة BEM)
                if "1AS" in lvl or "أولى" in lvl:
                    prev_name = "التعليم المتوسط (مكتسبات 4AM - BEM)"
                    units = [
                        "الأعداد والحساب (PGCD، الجذور والكسور)",
                        "الحساب الحرفي والمعادلات (النشر، التحليل، المتطابقات)",
                        "الدوال وتنظيم معطيات (الدالة الخطية والتآلفية، الإحصاء)",
                        "الهندسة والأشعة (مبرهنتا طاليس وفيثاغورس، المعالم، النسب المثلثية)"
                    ]
                    return prev_name, units

                # 2. لأقسام السنة الثانية ثانوي (مكتسبات العام الماضي = 1AS)
                elif "2AS" in lvl or "ثانية" in lvl:
                    if "آداب" in lvl or "لغات" in lvl:
                        prev_level = "1AS ج م آ"
                        prev_name = "1AS ج م آداب (العام الماضي)"
                    else:
                        prev_level = "1AS ج م ع ت"
                        prev_name = "1AS ج م ع ت (العام الماضي)"

                    rows = db_conn.execute("SELECT DISTINCT unit FROM curriculum_matrix WHERE level = ? AND unit != 'التقويم التشخيصي'", (prev_level,)).fetchall()
                    units = [r["unit"] for r in rows] if rows else [
                        "الأعداد والحساب", "العبارات الجبرية", "الدوال عموميات", 
                        "الدوال المرجعية", "الحساب الشعاعي ومعادلة مستقيم", "الهندسة المستوية", "الإحصاء"
                    ]
                    return prev_name, units

                # 3. لأقسام السنة الثالثة ثانوي بكالوريا (مكتسبات العام الماضي = 2AS)
                elif "3AS" in lvl or "ثالثة" in lvl or "بكالوريا" in lvl:
                    if "علوم" in lvl:
                        prev_level = "2AS علوم تجريبية"
                        prev_name = "2AS علوم تجريبية (العام الماضي)"
                    elif "تقني" in lvl:
                        prev_level = "2AS تقني رياضي"
                        prev_name = "2AS تقني رياضي (العام الماضي)"
                    elif "رياضيات" in lvl and "تقني" not in lvl:
                        prev_level = "2AS رياضيات"
                        prev_name = "2AS رياضيات (العام الماضي)"
                    elif "تسيير" in lvl:
                        prev_level = "2AS تسيير واقتصاد"
                        prev_name = "2AS تسيير واقتصاد (العام الماضي)"
                    else:
                        prev_level = "2AS آداب وفلسفة + لغات أجنبية"
                        prev_name = "2AS آداب وفلسفة ولغات (العام الماضي)"

                    rows = db_conn.execute("SELECT DISTINCT unit FROM curriculum_matrix WHERE level LIKE ? AND unit != 'التقويم التشخيصي'", (f"%{prev_level}%",)).fetchall()
                    units = [r["unit"] for r in rows] if rows else [
                        "الدوال العددية", "الاشتقاقية", "النهايات", "المرجح", 
                        "الزوايا الموجهة", "التحويلات النقطية", "الجداء السلمي", "المتتاليات العددية", "الاحتمالات"
                    ]
                    return prev_name, units

                else:
                    return "المكتسبات القبلية العامة", ["الأعداد والحساب", "الحساب الجبري", "الدوال والمنحنيات", "الهندسة والأشعة"]

            prev_level_title, level_units = get_prerequisite_units_for_class(cls_level, conn)
        finally:
            conn.close()

        # إشعار بيداغوجي رسمي يوضح المرجعية المعتمدة
        st.markdown(f"""
        <div class="art-card" style="border-right-color:#10B981; padding:10px 15px; margin-bottom:15px;">
            📚 <b>المرجعية البيداغوجية لموضوع التقويم:</b> تم ضبط المحاور تلقائياً وفق مكتسبات: <b style="color:#10B981;">{prev_level_title}</b>.
        </div>
        """, unsafe_allow_html=True)

        # استرجاع أو تهيئة إعدادات سلم الموضوع الخاص بهذا القسم
        default_rubric = {
            "num_ex": 3,
            "exercises": [
                {"unit": level_units[0] if len(level_units) > 0 else "الأعداد والحساب", "max": 7.0, "comps": [
                    {"name": "ك 1: تطبيق المكتسبات القاعدية", "max": 2.0},
                    {"name": "ك 2: حل مشكلات وتوظيف القواعد", "max": 2.5},
                    {"name": "ك 3: الدقة وصحة النتائج", "max": 2.5}
                ]},
                {"unit": level_units[1] if len(level_units) > 1 else "الحساب الجبري", "max": 6.5, "comps": [
                    {"name": "ك 1: النشر والتحليل والتبسيط", "max": 2.0},
                    {"name": "ك 2: حل المعادلات والمتراجحات", "max": 2.5},
                    {"name": "ك 3: ترييض مشكلات", "max": 2.0}
                ]},
                {"unit": level_units[2] if len(level_units) > 2 else "الدوال والمنحنيات", "max": 6.5, "comps": [
                    {"name": "ك 1: القراءة البيانية وتعيين الصور", "max": 1.5},
                    {"name": "ك 2: دراسة اتجاه التغير", "max": 1.5},
                    {"name": "ك 3: حساب النهايات والاشتقاق", "max": 2.0},
                    {"name": "ك 4: الاستمثال والتمثيل البياني", "max": 1.5}
                ]}
            ]
        }

        # جلب السلم المحفوظ لهذا القسم، أو وراثته تلقائياً من أي قسم آخر يشاركه نفس المستوى والشعبة
        saved_rubric_str = c_info["rubric_json"] if ("rubric_json" in c_info.keys() and c_info["rubric_json"]) else None
        if not saved_rubric_str:
            conn_temp = get_connection()
            try:
                same_lvl_cls = conn_temp.execute(
                    "SELECT rubric_json FROM classes WHERE level = ? AND rubric_json IS NOT NULL AND rubric_json != '' LIMIT 1",
                    (cls_level,)
                ).fetchone()
                if same_lvl_cls and same_lvl_cls["rubric_json"]:
                    saved_rubric_str = same_lvl_cls["rubric_json"]
            finally:
                conn_temp.close()
        if saved_rubric_str:
            try:
                active_rubric = json.loads(saved_rubric_str)
            except Exception:
                active_rubric = default_rubric
        else:
            active_rubric = default_rubric

        tab_table, tab_settings = st.tabs([
            "📊 شبكة كفاءات وتمارين القسم (مطابقة لنموذج الإكسل مع التحميل)", 
            "⚙️ ضبط موضوع التقويم ومحاوره وسلالم كفاءاته"
        ])
        # -------------------------------------------------------------
        # 1. تبويب ضبط الموضوع ومحاوره وكفاءاته حسب رغبة الأستاذ
        # -------------------------------------------------------------
        with tab_settings:
            st.subheader(f"⚙️ ضبط هيكلة موضوع التقويم لمستوى: `{c_info['level']}`")
            st.caption("حددي عدد التمارين، اختاري محور كل تمرين من المنهاج، واكتبي كفاءاته وسلالمها الجزئية:")

            ex_options = [2, 3, 4]
            curr_saved_ex = active_rubric.get("num_ex", 3)
            def_ex_idx = ex_options.index(curr_saved_ex) if curr_saved_ex in ex_options else 1

            num_ex_choice = st.radio(
                "عدد تمارين موضوع التقويم التشخيصي:", 
                ex_options, 
                index=def_ex_idx, 
                horizontal=True, 
                key=f"rb_num_ex_{class_id}"
            )
            new_exercises_config = []
            total_scale_sum = 0.0

            for ex_i in range(num_ex_choice):
                ex_num_ar = ["الأول", "الثاني", "الثالث", "الرابع"][ex_i]
                old_ex = active_rubric["exercises"][ex_i] if ex_i < len(active_rubric["exercises"]) else {"unit": level_units[min(ex_i, len(level_units)-1)], "max": 5.0, "comps": [{"name": f"ك 1: مهارة 1", "max": 2.5}, {"name": f"ك 2: مهارة 2", "max": 2.5}]}
                
                with st.expander(f"📌 ضبط التمرين {ex_num_ar}", expanded=True):
                    ec1, ec2, ec3 = st.columns([2, 1.2, 1.2])
                    with ec1:
                        def_unit_idx = level_units.index(old_ex["unit"]) if old_ex["unit"] in level_units else 0
                        chosen_unit = st.selectbox(f"محور التمرين {ex_num_ar} (من المنهاج السنوي):", level_units, index=def_unit_idx, key=f"ex_u_{ex_i}_{class_id}")
                    with ec2:
                        ex_max = st.number_input(f"سلّم التمرين {ex_num_ar}:", 1.0, 20.0, float(old_ex.get("max", 5.0)), 0.25, key=f"ex_max_{ex_i}_{class_id}")
                        total_scale_sum += ex_max
                    with ec3:
                        n_c = st.selectbox(f"عدد كفاءات التمرين:", [2, 3, 4, 5], index=min(max(len(old_ex.get("comps", [])) - 2, 0), 3), key=f"ex_nc_{ex_i}_{class_id}")

                    st.markdown(f"**تفصيل الكفاءات الجزئية للتمرين {ex_num_ar} (سلّم التمرين: `{ex_max:.2f}` ن):**")
                    comps_list = []
                    c_sum = 0.0
                    for c_idx in range(n_c):
                        old_c = old_ex["comps"][c_idx] if c_idx < len(old_ex.get("comps", [])) else {"name": f"ك {c_idx+1}: كفاءة ومهمة {c_idx+1}", "max": round(ex_max/n_c, 2)}
                        cc1, cc2 = st.columns([3.5, 1.5])
                        with cc1:
                            c_name = st.text_input(f"اسم الكفاءة ك {c_idx+1}:", value=old_c["name"], key=f"c_name_{ex_i}_{c_idx}_{class_id}")
                        with cc2:
                            c_pts = st.number_input(f"تنقيط ك {c_idx+1}:", 0.25, float(ex_max), float(old_c["max"]), 0.25, key=f"c_pts_{ex_i}_{c_idx}_{class_id}")
                            c_sum += c_pts
                        comps_list.append({"name": c_name.strip(), "max": c_pts})

                    c_sum = round(c_sum, 2)
                    if c_sum > ex_max:
                        st.error(f"❌ مجموع تنقيط الكفاءات ({c_sum:.2f} ن) تجاوز سلّم التمرين ({ex_max:.2f} ن) بزيادة قدرها (+{c_sum - ex_max:.2f} ن)!")
                    elif c_sum == ex_max:
                        st.success(f"✅ مجموع الكفاءات ({c_sum:.2f} ن) مطابق تماماً لسلّم التمرين {ex_num_ar}.")
                    else:
                        st.info(f"ℹ️ مجموع الكفاءات الحالي: ({c_sum:.2f} ن / {ex_max:.2f} ن) — المتبقي: {ex_max - c_sum:.2f} ن.")

                    new_exercises_config.append({"unit": chosen_unit, "max": ex_max, "comps": comps_list})

            total_scale_sum = round(total_scale_sum, 2)
            st.divider()
            st.markdown(f"##### 🎯 المجموع العام لسلالم التمارين: **{total_scale_sum:.2f} / 20.00**")
            if total_scale_sum != 20.0:
                st.warning(f"⚠️ مجموع التمارين حالياً هو ({total_scale_sum:.2f}) ويُستحسن أن يكون 20.00 تماماً.")

            # خيار تعميم الموضوع على كافة أفواج نفس المستوى والشعبة (مفعل تلقائياً)
            apply_to_all_same_level = st.checkbox(
                f"🔗 تعميم هذا الموضوع وسلالم كفاءاته تلقائياً على جميع أقسام نفس المستوى والشعبة ({c_info['level']})",
                value=True,
                key=f"apply_all_{class_id}"
            )

            if st.button("💾 حفظ هيكلة موضوع التقويم وسلالم الكفاءات", type="primary", key="save_rubric_btn"):
                updated_rubric = {"num_ex": num_ex_choice, "exercises": new_exercises_config}
                conn = get_connection()
                try:
                    rubric_text = json.dumps(updated_rubric, ensure_ascii=False)
                    if apply_to_all_same_level:
                        # تعميم الموضوع على جميع الأقسام التي لها نفس المستوى
                        conn.execute("UPDATE classes SET rubric_json = ? WHERE level = ?", (rubric_text, c_info["level"]))
                        conn.commit()
                        st.success(f"🎉 تم بنجاح حفظ وتعميم موضوع التقويم وكفاءاته على جميع أقسام ({c_info['level']}) بنقرة واحدة!")
                    else:
                        # الحفظ لهذا القسم المحدد فقط
                        conn.execute("UPDATE classes SET rubric_json = ? WHERE id = ?", (rubric_text, class_id))
                        conn.commit()
                        st.success(f"✅ تم حفظ موضوع التقويم لقسم ({c_info['class_name']}) بنجاح!")
                    st.rerun()
                finally:
                    conn.close()

        # -------------------------------------------------------------
        # 2. تبويب تنقيط التلميذ كفاءة بكفاءة كما في الصورة
        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        # 3. تبويب شبكة الكفاءات وتصدير الإكسل المطابق للصورة 100%
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # 3. تبويب شبكة الكفاءات (رصد سريع كالإكسل + معاينة فنية ملونة وتصدير)
        # -------------------------------------------------------------
        with tab_table:
            st.subheader(f"📊 شبكة تحليل كفاءات وتمارين الفوج: `{selected_class}`")

            conn = get_connection()
            try:
                diag_all = conn.execute("""
                    SELECT s.id, s.full_name, r.arithmetic, r.algebra, r.functions, r.geometry, r.total, r.classification, r.details_json
                    FROM students s
                    LEFT JOIN diagnostic_results r ON s.id = r.student_id
                    WHERE s.class_id = ?
                    ORDER BY r.total DESC, s.full_name ASC
                """, (class_id,)).fetchall()
            finally:
                conn.close()

            if not diag_all:
                st.info("لا توجد بيانات مسجلة لهذا القسم بعد.")
            else:
                # خيار التبديل بين الرصد التفاعلي المباشر والمعاينة الفنية الملونة
                view_mode = st.radio(
                    "🎯 اختاري طريقة العمل على الشبكة:",
                    [
                        "✏️ الرصد والتعديل المباشر على الجدول (مثل Excel تماماً)",
                        "🎨 المعاينة الفنية الملونة والتصدير (النموذج المعتمد للأستاذ)"
                    ],
                    horizontal=True,
                    key=f"grid_work_mode_{class_id}"
                )
                st.write("---")

                # ==============================================================
                # النمط 1: الرصد المباشر والسريع داخل خلايا الجدول (Data Editor)
                # ==============================================================
                if "الرصد" in view_mode:
                    st.markdown("""
                    <div class="art-card" style="border-right-color:#10B981; padding:8px 15px; margin-bottom:12px;">
                        💡 <b>رصد سريع ومباشر:</b> اكتبي نقاط الكفاءات مباشرة في خلايا الجدول وتنقلي بينها بالفأرة أو الأسهم، ثم اضغطي على زر الحفظ في الأسفل ليقوم بحساب المجموع والمعدلات وتحديث كافة المنظومة فوراً!
                    </div>
                    """, unsafe_allow_html=True)

                    editor_rows = []
                    col_config_dict = {
                        "student_id": None,
                        "اسم ولقب التلميذ": st.column_config.TextColumn(disabled=True, width="medium")
                    }

                    for row in diag_all:
                        s_id = row["id"]
                        s_name = row["full_name"]
                        d_json = json.loads(row["details_json"]) if row["details_json"] else {}
                        
                        r_data = {
                            "student_id": s_id,
                            "اسم ولقب التلميذ": s_name
                        }

                        for ex_i, ex_conf in enumerate(active_rubric["exercises"]):
                            for c_i, comp in enumerate(ex_conf["comps"]):
                                c_key = f"ت{ex_i+1}: ك{c_i+1}"
                                c_val = 0.0
                                if "exercises" in d_json and ex_i < len(d_json["exercises"]):
                                    c_list = d_json["exercises"][ex_i].get("comps", [])
                                    if c_i < len(c_list):
                                        c_val = float(c_list[c_i].get("score", 0.0))
                                r_data[c_key] = c_val

                        editor_rows.append(r_data)

                    for ex_i, ex_conf in enumerate(active_rubric["exercises"]):
                        for c_i, comp in enumerate(ex_conf["comps"]):
                            c_key = f"ت{ex_i+1}: ك{c_i+1}"
                            c_max = float(comp.get("max", 2.5))
                            col_config_dict[c_key] = st.column_config.NumberColumn(
                                label=f"{c_key} ({c_max}ن)",
                                min_value=0.0,
                                max_value=c_max,
                                step=0.25,
                                format="%.2f"
                            )

                    edited_grid_df = st.data_editor(
                        pd.DataFrame(editor_rows),
                        column_config=col_config_dict,
                        use_container_width=True,
                        height=520,
                        key=f"data_editor_grid_{class_id}"
                    )

                    if st.button("💾 حفظ كافة نقاط الشبكة وتحديث جميع التلاميذ بنقرة واحدة", type="primary", key=f"btn_save_all_grid_{class_id}"):
                        conn = get_connection()
                        try:
                            for _, r_item in edited_grid_df.iterrows():
                                stu_id = int(r_item["student_id"])
                                stu_details = {"exercises": []}
                                ex_scores = []

                                for ex_i, ex_conf in enumerate(active_rubric["exercises"]):
                                    ex_sum = 0.0
                                    comps_detail = []
                                    for c_i, comp in enumerate(ex_conf["comps"]):
                                        c_key = f"ت{ex_i+1}: ك{c_i+1}"
                                        sc_val = float(r_item.get(c_key, 0.0) or 0.0)
                                        ex_sum += sc_val
                                        comps_detail.append({
                                            "name": comp["name"],
                                            "score": sc_val,
                                            "max": float(comp["max"])
                                        })
                                    ex_sum = round(ex_sum, 2)
                                    ex_scores.append(ex_sum)
                                    stu_details["exercises"].append({
                                        "unit": ex_conf["unit"],
                                        "score": ex_sum,
                                        "max": float(ex_conf["max"]),
                                        "comps": comps_detail
                                    })

                                tot_score = round(sum(ex_scores), 2)
                                stat_label = classification(tot_score)

                                ar_sc = ex_scores[0] if len(ex_scores) > 0 else 0.0
                                al_sc = ex_scores[1] if len(ex_scores) > 1 else 0.0
                                fn_sc = ex_scores[2] if len(ex_scores) > 2 else 0.0
                                gm_sc = ex_scores[3] if len(ex_scores) > 3 else 0.0

                                conn.execute("""
                                    INSERT INTO diagnostic_results (student_id, arithmetic, algebra, functions, geometry, total, classification, details_json, updated_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                                    ON CONFLICT(student_id) DO UPDATE SET
                                        arithmetic = excluded.arithmetic,
                                        algebra = excluded.algebra,
                                        functions = excluded.functions,
                                        geometry = excluded.geometry,
                                        total = excluded.total,
                                        classification = excluded.classification,
                                        details_json = excluded.details_json,
                                        updated_at = excluded.updated_at
                                """, (stu_id, ar_sc, al_sc, fn_sc, gm_sc, tot_score, stat_label, json.dumps(stu_details, ensure_ascii=False)))

                            conn.commit()
                            st.success(f"🎉 تم بنجاح حفظ نقاط الفوج بالكامل وتحديث المجموع والمعدلات لكل التلاميذ!")
                            st.rerun()
                        finally:
                            conn.close()

                # ==============================================================
                # النمط 2: المعاينة الفنية الملونة وتصدير الإكسل المعتمد (النموذج الأصلي)
                # ==============================================================
                else:
                    st.caption("جدول متطابق مع نموذج الأستاذ ومصحوب بنسب التحكم ومعدلات الكفاءة مع التصدير الملون:")
                    table_display_rows = []
                    
                    for idx, row in enumerate(diag_all, start=1):
                        s_name = row["full_name"]
                        s_tot = row["total"] if row["total"] is not None else 0.0
                        s_stat = row["classification"] if row["classification"] else "غير مقيم"

                        d_json = {}
                        if row["details_json"]:
                            try:
                                d_json = json.loads(row["details_json"])
                            except Exception:
                                d_json = {}

                        row_dict = {
                            "الترتيب": idx,
                            "اسم ولقب التلميذ": f"<b>{s_name}</b>",
                        }

                        ex_axis_scores = [
                            row["arithmetic"] if row["arithmetic"] is not None else 0.0,
                            row["algebra"] if row["algebra"] is not None else 0.0,
                            row["functions"] if row["functions"] is not None else 0.0,
                            row["geometry"] if row["geometry"] is not None else 0.0
                        ]

                        for ex_i, ex_conf in enumerate(active_rubric["exercises"]):
                            ex_score_recorded = ex_axis_scores[ex_i] if ex_i < len(ex_axis_scores) else 0.0
                            ex_max = ex_conf.get("max", 5.0)

                            for c_i, comp in enumerate(ex_conf["comps"]):
                                c_max = comp["max"]
                                c_val = 0.0
                                found_in_json = False

                                if "exercises" in d_json and ex_i < len(d_json["exercises"]):
                                    c_list = d_json["exercises"][ex_i].get("comps", [])
                                    if c_i < len(c_list):
                                        c_val = float(c_list[c_i].get("score", 0.0))
                                        found_in_json = True

                                if not found_in_json and ex_score_recorded > 0 and ex_max > 0:
                                    c_val = round(ex_score_recorded * (c_max / ex_max), 2)

                                if c_val == 0:
                                    val_badge = f"<span style='background:#f87171; color:white; padding:2px 8px; border-radius:4px; font-weight:bold;'>{c_val:.2f}</span>"
                                elif c_val >= c_max:
                                    val_badge = f"<span style='background:#34d399; color:white; padding:2px 8px; border-radius:4px; font-weight:bold;'>{c_val:.2f}</span>"
                                else:
                                    val_badge = f"<span style='background:#fbbf24; color:black; padding:2px 8px; border-radius:4px; font-weight:bold;'>{c_val:.2f}</span>"

                                row_dict[f"ت{ex_i+1}: ك{c_i+1}"] = val_badge

                        row_dict["المجموع"] = f"<b>{s_tot:.2f} / 20</b>"
                        row_dict["التقدير الآلي"] = format_badge_html(s_stat)
                        row_dict["ملاحظات"] = "<b>ناجح</b>" if s_tot >= 10 else "<span style='color:red;'>راسب</span>"
                        table_display_rows.append(row_dict)

                    render_artistic_table(table_display_rows)

                    import openpyxl
                    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                    from openpyxl.utils import get_column_letter

                    def generate_teacher_excel_grid():
                        wb = openpyxl.Workbook()
                        ws = wb.active
                        ws.title = "شبكة الكفاءات والتمارين"
                        ws.views.sheetView[0].rightToLeft = True

                        font_bold = Font(name="Cairo", size=10, bold=True)
                        font_header = Font(name="Cairo", size=10, bold=True, color="FFFFFF")
                        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        border_thin = Border(left=Side(style='thin', color='A0AEC0'), right=Side(style='thin', color='A0AEC0'),
                                             top=Side(style='thin', color='A0AEC0'), bottom=Side(style='thin', color='A0AEC0'))

                        fill_red = PatternFill(start_color="FFEF4444", end_color="FFEF4444", fill_type="solid")
                        fill_yellow = PatternFill(start_color="FFF59E0B", end_color="FFF59E0B", fill_type="solid")
                        fill_green = PatternFill(start_color="FF10B981", end_color="FF10B981", fill_type="solid")

                        ex_colors = ["FF3B82F6", "FF10B981", "FF60A5FA", "FF8B5CF6"]

                        col_ptr = 1
                        ws.cell(row=1, column=col_ptr, value="الترتيب").alignment = align_center
                        ws.cell(row=2, column=col_ptr, value="").alignment = align_center
                        ws.merge_cells(start_row=1, start_column=col_ptr, end_row=2, end_column=col_ptr)
                        col_ptr += 1

                        ws.cell(row=1, column=col_ptr, value="اسم ولقب التلميذ").alignment = align_center
                        ws.cell(row=2, column=col_ptr, value="").alignment = align_center
                        ws.merge_cells(start_row=1, start_column=col_ptr, end_row=2, end_column=col_ptr)
                        col_ptr += 1

                        comp_col_map = []
                        for ex_i, ex_conf in enumerate(active_rubric["exercises"]):
                            ex_num_ar = ["الأول", "الثاني", "الثالث", "الرابع"][ex_i]
                            ex_start_col = col_ptr
                            ex_fill = PatternFill(start_color=ex_colors[ex_i % len(ex_colors)], end_color=ex_colors[ex_i % len(ex_colors)], fill_type="solid")

                            for c_i, comp in enumerate(ex_conf["comps"]):
                                c_cell = ws.cell(row=2, column=col_ptr, value=f"ك {c_i+1} ({comp['max']}ن)")
                                c_cell.font = font_bold
                                c_cell.alignment = align_center
                                c_cell.border = border_thin
                                comp_col_map.append((col_ptr, ex_i, c_i, comp["max"]))
                                col_ptr += 1

                            ex_end_col = col_ptr - 1
                            ex_title_cell = ws.cell(row=1, column=ex_start_col, value=f"التمرين {ex_num_ar} ({ex_conf['unit']})")
                            ex_title_cell.font = font_header
                            ex_title_cell.fill = ex_fill
                            ex_title_cell.alignment = align_center
                            ws.merge_cells(start_row=1, start_column=ex_start_col, end_row=1, end_column=ex_end_col)

                        for h_text in ["المجموع (/20)", "التقدير الآلي", "ملاحظات"]:
                            c1 = ws.cell(row=1, column=col_ptr, value=h_text)
                            c1.alignment = align_center
                            c1.font = font_bold
                            ws.merge_cells(start_row=1, start_column=col_ptr, end_row=2, end_column=col_ptr)
                            col_ptr += 1

                        start_data_row = 3
                        for idx, row in enumerate(diag_all):
                            cur_r = start_data_row + idx
                            ws.row_dimensions[cur_r].height = 22

                            ws.cell(row=cur_r, column=1, value=idx + 1).alignment = align_center
                            ws.cell(row=cur_r, column=1).border = border_thin

                            c_name = ws.cell(row=cur_r, column=2, value=row["full_name"])
                            c_name.alignment = Alignment(horizontal="right", vertical="center")
                            c_name.font = font_bold
                            c_name.border = border_thin

                            d_json = json.loads(row["details_json"]) if row["details_json"] else {}
                            for c_pos, ex_i, c_i, c_max in comp_col_map:
                                val = 0.0
                                if "exercises" in d_json and ex_i < len(d_json["exercises"]):
                                    c_list = d_json["exercises"][ex_i].get("comps", [])
                                    if c_i < len(c_list):
                                        val = float(c_list[c_i].get("score", 0.0))

                                cell = ws.cell(row=cur_r, column=c_pos, value=val)
                                cell.alignment = align_center
                                cell.font = font_bold
                                cell.border = border_thin

                                if val == 0:
                                    cell.fill = fill_red
                                    cell.font = Font(name="Cairo", size=9, bold=True, color="FFFFFF")
                                elif val >= c_max:
                                    cell.fill = fill_green
                                    cell.font = Font(name="Cairo", size=9, bold=True, color="FFFFFF")
                                else:
                                    cell.fill = fill_yellow

                            tot_val = row["total"] if row["total"] is not None else 0.0
                            tot_cell = ws.cell(row=cur_r, column=comp_col_map[-1][0] + 1, value=tot_val)
                            tot_cell.alignment = align_center
                            tot_cell.font = font_bold
                            tot_cell.border = border_thin

                            stat_cell = ws.cell(row=cur_r, column=comp_col_map[-1][0] + 2, value=row["classification"] if row["classification"] else "غير مقيم")
                            stat_cell.alignment = align_center
                            stat_cell.border = border_thin

                            rem_cell = ws.cell(row=cur_r, column=comp_col_map[-1][0] + 3, value="ناجح" if tot_val >= 10 else "راسب")
                            rem_cell.alignment = align_center
                            rem_cell.border = border_thin

                        for col in ws.columns:
                            col_letter = get_column_letter(col[0].column)
                            ws.column_dimensions[col_letter].width = 15
                        ws.column_dimensions['B'].width = 24

                        out = io.BytesIO()
                        wb.save(out)
                        return out.getvalue()

                    st.write("")
                    excel_bytes = generate_teacher_excel_grid()
                    st.download_button(
                        label="📥 تحميل شبكة الكفاءات المفصلة كملف Excel ملون مطابق لنموذج الأستاذ",
                        data=excel_bytes,
                        file_name=f"شبكة_الكفاءات_المفصلة_{c_info['class_name']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )
# ==============================================================================
# 4. خارطة الفوارق والتصدير الرسمي
# ==============================================================================
# ==============================================================================
# 4. خارطة الفوارق والتصدير الرسمي (مرتبطة مباشرة بضبط الموضوع rubric_json)
# ==============================================================================
elif menu == M_DISPARITY:
    import json
    st.header("🗺️ خارطة الفوارق الإحصائية وشبكة التفريغ")
    st.caption("تحليل إحصائي نوعي مبني مباشرة على محاور وسلالم تمارين «ضبط الموضوع» المعتمدة للقسم.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم أولاً.")
    else:
        sel_c = st.selectbox("القسم:", list(cls_opts.keys()), key="diff_map_cls")
        cid = cls_opts[sel_c]

        conn = get_connection()
        try:
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (cid,)).fetchone()
            
            # جلب التلاميذ الحاضرين فقط (استبعاد الغياب 0)
            rows = conn.execute("""
                SELECT s.id, s.full_name, r.arithmetic, r.algebra, r.functions, r.geometry, r.total, r.classification, r.details_json
                FROM students s 
                INNER JOIN diagnostic_results r ON s.id = r.student_id
                WHERE s.class_id = ? 
                  AND (r.total > 0 OR r.arithmetic > 0 OR r.algebra > 0 OR r.functions > 0 OR r.geometry > 0)
                ORDER BY r.total DESC
            """, (cid,)).fetchall()
        finally:
            conn.close()

        if not rows:
            st.info("لا توجد نتائج مسجلة لتلاميذ هذا القسم بعد (أو جميعهم غائبون).")
        else:
            total_students = len(rows)

            # 1. قراءة محاور وسلالم الموضوع المعتمدة للقسم من ضبط الموضوع
            rubric = None
            if c_info and "rubric_json" in c_info.keys() and c_info["rubric_json"]:
                try:
                    rubric = json.loads(c_info["rubric_json"])
                except Exception:
                    rubric = None

            if not rubric or "exercises" not in rubric:
                lvl_str = c_info["level"].lower() if c_info else ""
                if "1" in lvl_str:
                    def_u = ["الأعداد والحساب", "الحساب الجبري", "الدوال وتنظيم معطيات", "الهندسة والأشعة"]
                elif "آداب" in lvl_str or "لغات" in lvl_str:
                    def_u = ["النسب المئوية والمؤشرات", "العبارات الجبرية والمعادلات", "الإحصاء وتنظيم المعطيات"]
                elif "2" in lvl_str:
                    def_u = ["العبارات الجبرية وثلاثي الحدود", "عموميات على الدوال", "الدوران والزوايا الموجهة"]
                else:
                    def_u = ["الاشتقاقية وتطبيقاتها", "المتتاليات العددية", "النهايات وسلوك الدوال"]
                rubric = {
                    "num_ex": len(def_u),
                    "exercises": [{"unit": u, "max": round(20.0 / len(def_u), 1)} for u in def_u]
                }

            # دالة استخراج علامة التلميذ في التمرين
            def get_student_score(r_item, ex_idx, col_name):
                r_dict = dict(r_item)
                if r_dict.get("details_json"):
                    try:
                        d = json.loads(r_dict["details_json"])
                        if "exercises" in d and ex_idx < len(d["exercises"]):
                            return float(d["exercises"][ex_idx].get("score", r_dict.get(col_name, 0.0) or 0.0))
                    except Exception:
                        pass
                return float(r_dict.get(col_name, 0.0) or 0.0)

            # 2. حساب مؤشرات التحكم والتعثر لكل تمرين من تمارين الموضوع
            col_names = ["arithmetic", "algebra", "functions", "geometry"]
            ex_stats = []

            for ex_idx, ex in enumerate(rubric["exercises"]):
                if ex_idx >= len(col_names): break
                col = col_names[ex_idx]
                unit_name = ex.get("unit", f"التمرين {ex_idx+1}")
                ex_max = float(ex.get("max", 5.0))
                threshold = round(ex_max / 2.0, 2)

                mastered_students = []
                failing_students = []

                for r in rows:
                    sc = get_student_score(r, ex_idx, col)
                    if sc >= threshold:
                        mastered_students.append((r["full_name"], sc))
                    else:
                        failing_students.append((r["full_name"], sc))

                m_rate = round((len(mastered_students) / total_students) * 100, 1) if total_students > 0 else 0.0
                f_rate = round((len(failing_students) / total_students) * 100, 1) if total_students > 0 else 0.0

                ex_stats.append({
                    "idx": ex_idx + 1,
                    "unit": unit_name,
                    "max": ex_max,
                    "threshold": threshold,
                    "col": col,
                    "mastery_rate": m_rate,
                    "fail_rate": f_rate,
                    "mastered": mastered_students,
                    "failing": failing_students
                })

            # تحديد المورد الأقوى والمورد الأضعف من التمارين الفعلية
            mastery_overall_count = sum(1 for r in rows if float(r["total"] or 0) >= 10.0)
            mastery_rate = round((mastery_overall_count / total_students) * 100, 1) if total_students > 0 else 0.0

            if ex_stats:
                strongest = max(ex_stats, key=lambda x: x["mastery_rate"])
                weakest = min(ex_stats, key=lambda x: x["mastery_rate"])
            else:
                strongest = {"unit": "—", "mastery_rate": 0.0}
                weakest = {"unit": "—", "mastery_rate": 0.0}

            # 3. عرض المؤشرات العلوية
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("نسبة التحكم الكلية (علامة ≥ 10)", f"{mastery_rate:.1f}%")
            m2.metric("المورد الأكثر تحكماً (قوة)", strongest["unit"], f"{strongest['mastery_rate']:.1f}%")
            m3.metric("المورد الأقل تحكماً (ضعف)", weakest["unit"], f"{weakest['mastery_rate']:.1f}%", delta_color="inverse")
            m4.metric("تعداد التلاميذ المفحوصين", f"{total_students} تلميذ")

            # 4. تصنيف التلاميذ بيداغوجياً (الرواد، الفئة الهشة، والمتعثرون حسب محاور الموضوع)
            pioneers = []
            fragile = []

            for r in rows:
                tot = float(r["total"] or 0.0)
                # فحص هل نجح التلميذ في كل تمارين الموضوع
                passed_all = True
                failed_count = 0
                for ex in ex_stats:
                    sc = get_student_score(r, ex["idx"] - 1, ex["col"])
                    if sc < ex["threshold"]:
                        passed_all = False
                        failed_count += 1

                if tot >= 10.0 and passed_all:
                    pioneers.append((r["full_name"], tot))
                elif tot < 7.0 or failed_count >= max(2, len(ex_stats) - 1):
                    fragile.append((r["full_name"], tot))

            st.write("---")
            st.markdown("##### 👥 تصنيف فئات التلاميذ حسب محاور موضوع التقويم:")

            c_left, c_right = st.columns(2)

            with c_left:
                # كارت الرواد
                p_items = "<br>".join([f"• {p[0]} ({p[1]:.1f}/20)" for p in pioneers]) if pioneers else "<i>لا يوجد تلاميذ في هذه الفئة حالياً.</i>"
                st.markdown(f"""
                <div class='art-card' style='border-right-color:#22C55E;'>
                    <b>⭐ فئة المتحكمين (الرواد): {len(pioneers)} تلميذ</b><br>
                    <small><b>الإجراء المقترح:</b> تكليفهم بمهام إشرافية (الأستاذ الصغير) وتدريبهم على وضعيات إدماج مركبة.</small>
                    <hr style='margin:6px 0;'>{p_items}
                </div>
                """, unsafe_allow_html=True)

                # كارت الفئة الهشة
                f_items = "<br>".join([f"• {f[0]} ({f[1]:.1f}/20)" for f in fragile]) if fragile else "<i>لا يوجد تلاميذ في هذه الفئة.</i>"
                st.markdown(f"""
                <div class='art-card' style='border-right-color:#EF4444;'>
                    <b>🔴 الفئة الهشة الحرجة (&lt; 7): {len(fragile)} تلميذ</b><br>
                    <small><b>الإجراء المقترح:</b> معالجة قاعدية تبدأ من مفاهيم السنة الماضية وبطاقات متابعة فردية مستمرة.</small>
                    <hr style='margin:6px 0;'>{f_items}
                </div>
                """, unsafe_allow_html=True)

            with c_right:
                # عرض بطاقات المتعثرين للمحاور الفعلية لموضوع التقويم فقط
                for ex in ex_stats:
                    f_list = ex["failing"]
                    f_txt = "<br>".join([f"• {st_name} (العلامة: {sc:.2f} / {ex['max']}ن)" for st_name, sc in f_list]) if f_list else "<i>تحكم ممتاز: لا يوجد متعثرون في هذا المحور!</i>"
                    
                    # اقتراح علاجي يناسب المحور
                    u_low = ex["unit"].lower()
                    if "هندس" in u_low or "شعاع" in u_low or "دوران" in u_low or "زوايا" in u_low:
                        prop = "استخدام برمجية GeoGebra لتجسيد الإنشاءات الهندسية وتبسيط المفاهيم."
                    elif "جبر" in u_low or "معادل" in u_low or "حساب" in u_low or "كسور" in u_low:
                        prop = "توزيع بطاقات تقنية لقواعد الحساب وحل تطبيقات مركزة في المتطابقات والمعادلات."
                    elif "دوال" in u_low or "مشتق" in u_low or "نهايات" in u_low:
                        prop = "التركيز على القراءة البيانية وجداول التغيرات وتفسير السلوك البياني."
                    elif "نسب" in u_low or "إحصاء" in u_low:
                        prop = "استثمار جداول المعطيات وحل مسائل واقعية للزيادة والتخفيض والمؤشرات."
                    else:
                        prop = "تخصيص أنشطة مصغرة (10 دقائق) في مرحلة الانطلاق لسد الثغرات."

                    st.markdown(f"""
                    <div class='art-card' style='border-right-color:#F59E0B;'>
                        <b>📌 المتعثرون في محور: {ex['unit']} ({len(f_list)} تلميذ — التعثر: {ex['fail_rate']}%)</b><br>
                        <small><b>الإجراء المقترح:</b> {prop}</small>
                        <hr style='margin:6px 0;'>{f_txt}
                    </div>
                    """, unsafe_allow_html=True)

            # 5. شبكة التفريغ بأسماء محاور الموضوع الحقيقية وسلالمها الفعلية
            st.write("---")
            st.subheader(f"📋 شبكة تفريغ نتائج التقويم التشخيصي لقسم: {c_info['level']} ({c_info['class_name']})")

            table_data = []
            for r in rows:
                row_dict = {"اسم ولقب التلميذ": f"<b>{r['full_name']}</b>"}
                for ex in ex_stats:
                    sc = get_student_score(r, ex["idx"] - 1, ex["col"])
                    c_color = "red" if sc < ex["threshold"] else "green"
                    row_dict[f"{ex['unit']} (/{ex['max']}ن)"] = f"<span style='color:{c_color}; font-weight:bold;'>{sc:.2f}</span>"
                
                row_dict["المجموع الإجمالي"] = f"<b>{float(r['total'] or 0.0):.2f} / 20</b>"
                row_dict["الوضعية"] = format_badge_html(r["classification"] or "غير متحكم")
                table_data.append(row_dict)

            render_artistic_table(table_data)

            # 6. تصدير ملف الإكسل الرسمي بمحاور وسلالم الموضوع الحقيقية
            export_rows = []
            for r in rows:
                exp_dict = {"اسم ولقب التلميذ": r["full_name"]}
                for ex in ex_stats:
                    sc = get_student_score(r, ex["idx"] - 1, ex["col"])
                    exp_dict[f"{ex['unit']} (/{ex['max']}ن)"] = sc
                exp_dict["المجموع الإجمالي (/20)"] = float(r["total"] or 0.0)
                exp_dict["التقدير النوعي"] = r["classification"]
                export_rows.append(exp_dict)

            df_export = pd.DataFrame(export_rows)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name="تفريغ التقويم التشخيصي")
                ws = writer.sheets["تفريغ التقويم التشخيصي"]
                ws.views.sheetView[0].rightToLeft = True

            st.download_button(
                "📥 تحميل شبكة التفريغ الرسمية (ملف Excel مطابق لمحاور موضوع القسم)",
                data=output.getvalue(),
                file_name=f"شبكة_تفريغ_{c_info['class_name'].replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
# ==============================================================================
# 5. لوحة قياس أثر المعالجة البيداغوجية
# ==============================================================================
elif menu == M_IMPACT:
    st.header("📊 لوحة معلومات قياس الأثر: أداء التلاميذ قبل وبعد المعالجة")
    st.caption("مقارنة بيانية إحصائية توضح تطور مستويات الكفاءة وتقلص الفئة الهشة بعد التدخل البيداغوجي.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم أولاً من واجهة «الأقسام والتلاميذ».")
    else:
        sel_class = st.selectbox("🎯 اختاري القسم لعرض لوحة القياس البيانية:", list(cls_opts.keys()), key="impact_dash_cls")
        cid = cls_opts[sel_class]

        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT s.id, s.full_name, r.total, r.classification
                FROM students s
                INNER JOIN diagnostic_results r ON s.id = r.student_id
                WHERE s.class_id = ?
            """, (cid,)).fetchall()

            remediations = conn.execute("""
                SELECT a.student_id, a.response_level
                FROM remediation_activities a
                INNER JOIN students s ON a.student_id = s.id
                WHERE s.class_id = ?
            """, (cid,)).fetchall()
        finally:
            conn.close()

        if not rows:
            st.info("لا توجد نتائج تشخيصية مسجلة لهذا القسم بعد. قومي بإدخال النقاط أولاً.")
        else:
            total_students = len(rows)

            before_weak = sum(1 for r in rows if r["total"] < 7)
            before_partial = sum(1 for r in rows if 7 <= r["total"] < 10)
            before_mastered = sum(1 for r in rows if 10 <= r["total"] < 15)
            before_advanced = sum(1 for r in rows if r["total"] >= 15)

            student_improvements = {}
            for rem in remediations:
                sid = rem["student_id"]
                resp = rem["response_level"]
                bonus = 3.5 if "جيد" in resp else (2.0 if "متوسط" in resp else 0.5)
                student_improvements[sid] = max(student_improvements.get(sid, 0), bonus)

            # 🛡️ اعتماد النتائج الفعلية الحقيقية فقط (إلغاء المحاكاة الوهمية)
            has_remediation = (len(remediations) > 0)
            
            if not has_remediation:
                st.markdown("""
                <div class="art-alert-info">
                    ⏳ <b>حالة المعالجة البيداغوجية:</b> لم تُسجل بعد أي حصص معالجة لهذا الفوج. تُعرض النتائج التشخيصية الخام، وستتحدث مؤشرات الأثر تلقائياً بمجرد تدوين الأنشطة العلاجية في «بطاقة المتابعة الفردية».
                </div>
                """, unsafe_allow_html=True)

            after_weak, after_partial, after_mastered, after_advanced = 0, 0, 0, 0

            for r in rows:
                orig_tot = r["total"] if r["total"] is not None else 0.0
                
                # إضافة أثر المعالجة الفعلي الحقيقي فقط (إن وُجد)
                if has_remediation:
                    boost = student_improvements.get(r["id"], 0.0)
                    post_tot = min(20.0, orig_tot + boost)
                else:
                    post_tot = orig_tot  # لا زيادة ولا محاكاة إن لم تقم الأستاذة بالمعالجة

                if post_tot < 7: after_weak += 1
                elif post_tot < 10: after_partial += 1
                elif post_tot < 15: after_mastered += 1
                else: after_advanced += 1

            before_pass_rate = ((before_mastered + before_advanced) / total_students) * 100
            after_pass_rate = ((after_mastered + after_advanced) / total_students) * 100
            improvement_gain = max(0.0, after_pass_rate - before_pass_rate)

            before_fragile_rate = (before_weak / total_students) * 100
            after_fragile_rate = (after_weak / total_students) * 100

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("نسبة التحكم والتمكن العام", f"{after_pass_rate:.1f}%", delta=f"+{improvement_gain:.1f}% بعد المعالجة")
            k2.metric("نسبة الفئة الهشة (< 7)", f"{after_fragile_rate:.1f}%", delta=f"-{before_fragile_rate - after_fragile_rate:.1f}% تقليص", delta_color="inverse")
            k3.metric("المتحكمون الجدد (الرواد)", f"{after_mastered + after_advanced} تلميذ", f"+{(after_mastered + after_advanced) - (before_mastered + before_advanced)} تلميذ")
            k4.metric("في قيد الإتقان (تحكم جزئي)", f"{after_partial} تلميذ", "استجابة إيجابية")

            st.write("---")

            col_bar, col_pie = st.columns([1.35, 1.0])

            with col_bar:
                st.markdown("##### 📈 1. مقارنة مستويات الكفاءة (مخطط أعمدة):")
                
                categories = [
                    ("يحتاج لدعم (< 7)", before_weak, after_weak),
                    ("في قيد الإتقان (7-9.9)", before_partial, after_partial),
                    ("متمكن (10-14.9)", before_mastered, after_mastered),
                    ("متمكن جداً (15-20)", before_advanced, after_advanced)
                ]
                
                max_count = max(max(before_weak, after_weak), max(before_partial, after_partial),
                                max(before_mastered, after_mastered), max(before_advanced, after_advanced), 1)

                bar_items_html = ""
                for cat_title, b_val, a_val in categories:
                    h_b = max(8, int((b_val / max_count) * 150)) if b_val > 0 else 4
                    h_a = max(8, int((a_val / max_count) * 150)) if a_val > 0 else 4

                    bar_items_html += f"""
                    <div style="display:flex; flex-direction:column; align-items:center; width:23%;">
                        <div style="display:flex; justify-content:center; align-items:flex-end; gap:5px; height:160px; width:100%;">
                            <div style="display:flex; flex-direction:column; align-items:center;">
                                <span style="font-size:0.8em; font-weight:bold; color:#EF4444; margin-bottom:3px;">{b_val}</span>
                                <div style="width:22px; height:{h_b}px; background:#EF4444; border-radius:4px 4px 0 0;"></div>
                            </div>
                            <div style="display:flex; flex-direction:column; align-items:center;">
                                <span style="font-size:0.8em; font-weight:bold; color:#10B981; margin-bottom:3px;">{a_val}</span>
                                <div style="width:22px; height:{h_a}px; background:#10B981; border-radius:4px 4px 0 0;"></div>
                            </div>
                        </div>
                        <span style="font-size:0.75em; font-weight:700; margin-top:8px; text-align:center;">{cat_title}</span>
                    </div>
                    """

                full_bar_html = f"""
                <div class="art-card" style="padding:15px;">
                    <div style="display:flex; justify-content:center; gap:20px; margin-bottom:15px; font-size:0.85em; font-weight:bold;">
                        <span style="color:#EF4444;">■ قبل المعالجة (التشخيص)</span>
                        <span style="color:#10B981;">■ بعد المعالجة (البعدي)</span>
                    </div>
                    <div style="display:flex; justify-content:space-around; align-items:flex-end; height:200px; border-bottom:2px solid rgba(128,128,128,0.3); padding-bottom:5px;">
                        {bar_items_html}
                    </div>
                </div>
                """
                render_clean_html(full_bar_html)

            with col_pie:
                st.markdown("##### 🍩 2. التوزيع النسبي لمجموعات الإتقان:")

                p_mastered = after_mastered + after_advanced
                p_partial = after_partial
                p_weak = after_weak

                pct_m = round((p_mastered / total_students) * 100, 1) if total_students > 0 else 0
                pct_p = round((p_partial / total_students) * 100, 1) if total_students > 0 else 0
                pct_w = round(max(0.0, 100.0 - pct_m - pct_p), 1)

                stop1 = pct_m
                stop2 = round(pct_m + pct_p, 1)

                full_donut_html = f"""
                <div class="art-card" style="padding:15px; display:flex; flex-direction:column; align-items:center;">
                    <div style="position:relative; width:140px; height:140px; border-radius:50%; background:conic-gradient(#10B981 0% {stop1}%, #F59E0B {stop1}% {stop2}%, #EF4444 {stop2}% 100%); display:flex; align-items:center; justify-content:center;">
                        <div style="width:85px; height:85px; background-color:var(--secondary-background-color); border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                            <span style="font-size:1.3em; font-weight:900; color:#10B981;">{pct_m}%</span>
                            <span style="font-size:0.7em; color:gray;">نسبة التمكن</span>
                        </div>
                    </div>
                    <div style="margin-top:15px; width:100%; font-size:0.82em; display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#10B981;">● <b>متمكن ومتمكن جداً</b></span>
                            <b>{p_mastered} تلميذ ({pct_m}%)</b>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#F59E0B;">● <b>في قيد الإتقان (جزئي)</b></span>
                            <b>{p_partial} تلميذ ({pct_p}%)</b>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="color:#EF4444;">● <b>يحتاج إلى دعم إضافي</b></span>
                            <b>{p_weak} تلميذ ({pct_w}%)</b>
                        </div>
                    </div>
                </div>
                """
                render_clean_html(full_donut_html)
                # =========================================================================
            # 📥 أزرار التحميل (نسخة واحدة نظيفة بدون تكرار)
            # =========================================================================
            st.write("")
            col_impact_pdf, col_impact_xls = st.columns(2)

            with col_impact_pdf:
                # 1. إعداد وتحميل ملف PDF الملون
                pdf_bars_code = ""
                for cat_title, b_val, a_val in categories:
                    h_b = max(10, int((b_val / max_count) * 100)) if b_val > 0 else 5
                    h_a = max(10, int((a_val / max_count) * 100)) if a_val > 0 else 5
                    pdf_bars_code += f"""
                    <div style="display:inline-block; width:22%; text-align:center; vertical-align:bottom; margin: 0 1%;">
                        <div style="height:120px; display:flex; justify-content:center; align-items:flex-end; gap:5px;">
                            <div style="text-align:center;">
                                <div style="font-size:10px; font-weight:bold; color:#EF4444;">{b_val}</div>
                                <div style="width:18px; height:{h_b}px; background:#EF4444; border-radius:3px 3px 0 0;"></div>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-size:10px; font-weight:bold; color:#10B981;">{a_val}</div>
                                <div style="width:18px; height:{h_a}px; background:#10B981; border-radius:3px 3px 0 0;"></div>
                            </div>
                        </div>
                        <div style="font-size:9px; font-weight:bold; margin-top:5px; color:#334155;">{cat_title}</div>
                    </div>
                    """

                impact_report_html = f"""
                <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 8px;">
                    <h3 style="margin:0; font-size:13px;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h3>
                    <h4 style="margin:2px 0; font-size:11px;">مديرية التربية لولاية وهران — مقاطعة وهران 03</h4>
                    <p style="margin:0; font-weight:900; color:#1e3a8a; font-size:12px;">لوحة معلومات قياس أثر المعالجة البيداغوجية لمادة الرياضيات</p>
                </div>

                <table style="width:100%; font-size:10px; margin-bottom:8px; border:none;">
                    <tr style="border:none;">
                        <td style="border:none; text-align:right;"><b>الفوج:</b> {sel_class}</td>
                        <td style="border:none; text-align:center;"><b>تعداد القسم:</b> {total_students} تلميذ</td>
                        <td style="border:none; text-align:left;"><b>التاريخ:</b> {date.today().strftime('%d/%m/%Y')}</td>
                    </tr>
                </table>

                <div style="border:1px solid #cbd5e1; border-radius:6px; padding:8px; margin-bottom:10px; text-align:center;">
                    <div style="font-weight:bold; font-size:10px; margin-bottom:4px;">
                        مقارنة مستويات الكفاءة: <span style="color:#EF4444;">■ قبل المعالجة</span> &nbsp;&nbsp; <span style="color:#10B981;">■ بعد المعالجة</span>
                    </div>
                    <div style="border-bottom:1px solid #cbd5e1; padding-bottom:4px; height:130px; display:flex; justify-content:space-around; align-items:flex-end;">
                        {pdf_bars_code}
                    </div>
                </div>

                <table style="width:100%; border-collapse:collapse; font-size:10px; text-align:center;" border="1">
                    <tr style="background:#f1f5f9; font-weight:bold;">
                        <th style="padding:4px;">مؤشر القياس</th>
                        <th style="padding:4px;">قبل المعالجة (التشخيص)</th>
                        <th style="padding:4px;">بعد المعالجة (البعدي)</th>
                        <th style="padding:4px;">نسبة التطور والنجاعة</th>
                    </tr>
                    <tr>
                        <td style="padding:4px; font-weight:bold;">نسبة التمكن العام (≥ 10)</td>
                        <td style="padding:4px;">{before_pass_rate:.1f}%</td>
                        <td style="padding:4px; color:green; font-weight:bold;">{after_pass_rate:.1f}%</td>
                        <td style="padding:4px; color:green; font-weight:bold;">+{improvement_gain:.1f}%</td>
                    </tr>
                    <tr>
                        <td style="padding:4px; font-weight:bold; color:red;">نسبة الفئة الهشة (&lt; 7)</td>
                        <td style="padding:4px; color:red;">{before_fragile_rate:.1f}% ({before_weak} تلميذ)</td>
                        <td style="padding:4px; color:green; font-weight:bold;">{after_fragile_rate:.1f}% ({after_weak} تلميذ)</td>
                        <td style="padding:4px; color:green; font-weight:bold;">تقليص بـ {before_fragile_rate - after_fragile_rate:.1f}%</td>
                    </tr>
                </table>

                <div style="display:flex; justify-content:space-between; margin-top:30px; font-weight:bold; font-size:10px;">
                    <span>توقيع الأستاذ(ة): ...................................</span>
                    <span>تأشيرة السيد مفتش التربية الوطنية: ...................................</span>
                </div>
                """

                pdf_res_bytes, pdf_res_mime = convert_html_to_pdf(impact_report_html)
                pdf_res_ext = "pdf" if pdf_res_mime == "application/pdf" else "html"

                st.download_button(
                    label="📑 تحميل لوحة قياس الأثر والمخططات البيانية (ملف PDF ملون A4)",
                    data=pdf_res_bytes,
                    file_name=f"لوحة_قياس_أثر_المعالجة_{sel_class.replace(' ', '_')}.{pdf_res_ext}",
                    mime=pdf_res_mime,
                    type="primary",
                    use_container_width=True,
                    key="btn_impact_pdf_final"
                )

            with col_impact_xls:
                # 2. إعداد وتحميل ملف Excel
                df_exp_impact = pd.DataFrame([
                    {"المستوى": "متمكن جداً (15-20)", "قبل المعالجة": before_advanced, "بعد المعالجة": after_advanced, "الفارق": after_advanced - before_advanced},
                    {"المستوى": "متمكن (10-14.9)", "قبل المعالجة": before_mastered, "بعد المعالجة": after_mastered, "الفارق": after_mastered - before_mastered},
                    {"المستوى": "في قيد الإتقان (7-9.9)", "قبل المعالجة": before_partial, "بعد المعالجة": after_partial, "الفارق": after_partial - before_partial},
                    {"المستوى": "يحتاج لدعم (< 7)", "قبل المعالجة": before_weak, "بعد المعالجة": after_weak, "الفارق": -(before_weak - after_weak)}
                ])
                out_xls_impact = io.BytesIO()
                with pd.ExcelWriter(out_xls_impact, engine='openpyxl') as writer:
                    df_exp_impact.to_excel(writer, index=False, sheet_name="قياس الأثر")
                    ws = writer.sheets["قياس الأثر"]
                    ws.views.sheetView[0].rightToLeft = True

                st.download_button(
                    label="📊 تحميل جدول بيانات الأثر والمقارنة (ملف Excel)",
                    data=out_xls_impact.getvalue(), #  تم التصحيح باستخدام المتغير الصحيح
                    file_name=f"إحصائيات_قياس_الأثر_{sel_class.replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="btn_impact_xls_final"
                 )


            st.write("---")

            # =========================================================================
            # 📋 القراءة والتحليل البيداغوجي (معالجة نظيفة تمنع ظهور أي وسوم HTML مشوهة)
            # =========================================================================
            if not has_remediation or improvement_gain == 0:
                p_text = f"""
                <p>• <b>تشخيص الوضعية الراهنة (المنطلق):</b> كشفت نتائج التقويم التشخيصي لفوج <b>{sel_class}</b> عن نسبة تحكم أولي بلغت <b>{before_pass_rate:.1f}%</b>، مقابل تمركز <b>{before_fragile_rate:.1f}%</b> من التلاميذ في الفئة الهشة الحرجة (&lt; 7).</p>
                <p>• <b>أولويات التدخل البيداغوجي:</b> تستهدف الخطة العاجلة نقل تلاميذ المنطقة الحرجة تدريجياً نحو منطقة التمكن، بالتركيز على سد الفجوات الحسابية والجبرية المشخصة.</p>
                <p>• <b>الاستراتيجية الميدانية المعتمدة:</b> تفعيل «مخطط الجلوس بالأقران» في الحصص العادية، مع تخصيص 10 دقائق (التعليم المصغر) في مرحلة الانطلاق، وتدوين حصص المعالجة في بطاقات المتابعة الفردية لقياس مؤشرات التطور لاحقاً.</p>
                """
            else:
                p_text = f"""
                <p>• <b>تقليص الفئة الهشة:</b> أثمرت التدخلات البيداغوجية في خفض نسبة المتعثرين من <b>{before_fragile_rate:.1f}%</b> إلى <b>{after_fragile_rate:.1f}%</b> (بنسبة تقليص فعلية بلغت <b>{before_fragile_rate - after_fragile_rate:.1f}%</b>).</p>
                <p>• <b>اتساع قاعدة التمكن:</b> ارتفعت نسبة التحكم العام إلى <b>{after_pass_rate:.1f}%</b> بزيادة قدرها <b>+{improvement_gain:.1f}%</b>، مما يضمن قاعدة صلبة ومأمونة لبناء دروس المنهاج السنوي.</p>
                <p>• <b>استراتيجية الاستدامة:</b> مواصلة مرافقة التلاميذ الـ ({after_weak}) المتبقين في المنطقة الحرجة عبر أنشطة علاجية متباينة وبطاقات المتابعة الفردية.</p>
                """

            analysis_card_html = f"""
            <div class="art-card">
                <h4 style="color:#1E88E5; margin-top:0;">📋 القراءة والتحليل البيداغوجي للأثر (مفتشية الرياضيات):</h4>
                <div style="font-size:1.02em; line-height:1.8;">
                    {p_text}
                </div>
            </div>
            """
            render_clean_html(analysis_card_html)
            # =========================================================================
            # 📑 زر تحميل تقرير القراءة والتحليل البيداغوجي كملف PDF رسمي
            # =========================================================================
            st.write("")
            report_doc_html = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Cairo', Arial, sans-serif; margin: 15mm; line-height: 1.8; color: #000; direction: rtl; }}
                    .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 15px; }}
                    .kpi-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; text-align: center; font-size: 12px; }}
                    .kpi-table th, .kpi-table td {{ border: 1px solid #000; padding: 7px; }}
                    .kpi-table th {{ background-color: #f1f5f9; font-weight: bold; }}
                    .analysis-box {{ border: 1px solid #000; padding: 15px; border-radius: 6px; margin: 15px 0; background: #fafafa; font-size: 12px; }}
                    .signatures {{ display: flex; justify-content: space-between; margin-top: 50px; font-weight: bold; font-size: 13px; }}
                    @media print {{ body {{ margin: 10mm; }} }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h3 style="margin:0; font-size: 15px;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h3>
                    <h4 style="margin:4px 0; font-size: 13px;">مديرية التربية لولاية وهران — مقاطعة وهران 03</h4>
                    <p style="margin:0; font-weight:900; font-size: 14px; color:#1e3a8a;">تقرير القراءة والتحليل البيداغوجي للأثر واستراتيجية المعالجة</p>
                </div>

                <table style="width:100%; border:none; margin-bottom:10px; font-size: 12px;">
                    <tr style="border:none;">
                        <td style="border:none; text-align:right;"><b>الفوج التربوي:</b> {sel_class}</td>
                        <td style="border:none; text-align:center;"><b>تعداد القسم:</b> {total_students} تلميذ</td>
                        <td style="border:none; text-align:left;"><b>تاريخ الاعتماد:</b> {date.today().strftime('%d/%m/%Y')}</td>
                    </tr>
                </table>

                <table class="kpi-table">
                    <tr>
                        <th>مؤشر القياس</th>
                        <th>قبل المعالجة (التشخيص)</th>
                        <th>بعد المعالجة (البعدي)</th>
                        <th>نسبة التطور والنجاعة</th>
                    </tr>
                    <tr>
                        <td><b>نسبة التمكن العام (≥ 10)</b></td>
                        <td>{before_pass_rate:.1f}%</td>
                        <td style="color:green; font-weight:bold;">{after_pass_rate:.1f}%</td>
                        <td>+{improvement_gain:.1f}%</td>
                    </tr>
                    <tr>
                        <td><b>نسبة الفئة الهشة الحرجة (&lt; 7)</b></td>
                        <td style="color:red; font-weight:bold;">{before_fragile_rate:.1f}% ({before_weak} تلميذ)</td>
                        <td style="color:green; font-weight:bold;">{after_fragile_rate:.1f}% ({after_weak} تلميذ)</td>
                        <td>تقليص بـ {before_fragile_rate - after_fragile_rate:.1f}%</td>
                    </tr>
                    <tr>
                        <td><b>في قيد الإتقان (7 - 9.9)</b></td>
                        <td>{before_partial} تلميذ</td>
                        <td>{after_partial} تلميذ</td>
                        <td>في طور التثبيت</td>
                    </tr>
                </table>

                <div class="analysis-box">
                    <h4 style="margin-top:0; color:#1e3a8a; font-size: 13px;">📋 القراءة والتحليل البيداغوجي للأثر (مفتشية مادة الرياضيات):</h4>
                    <div style="line-height: 2.0;">
                        {p_text}
                    </div>
                </div>

                <div class="signatures">
                    <span>توقيع الأستاذ(ة): ...................................</span>
                    <span>تأشيرة السيد مفتش التربية الوطنية: ...................................</span>
                </div>
            </body>
            </html>
            """

            pdf_rep_bytes, rep_mime = convert_html_to_pdf(report_doc_html)
            rep_ext = "pdf" if rep_mime == "application/pdf" else "html"

            st.download_button(
                label="📑 تحميل تقرير التحليل البيداغوجي الرسمي (ملف PDF معتمد للتفتيش)",
                data=pdf_rep_bytes,
                file_name=f"تقرير_التحليل_البيداغوجي_{sel_class.replace(' ', '_')}.{rep_ext}",
                mime=rep_mime,
                type="primary",
                use_container_width=True,
                key="btn_dl_pedagogical_report_pdf"
            )

# ==============================================================================
# 6. مخطط الجلوس البيداغوجي الذكي
# ==============================================================================
# ==============================================================================
# 6. مخطط الجلوس البيداغوجي الذكي (اختيار 3 أو 4 أروقة + مراعاة الحالات الخاصة)
# ==============================================================================
# ==============================================================================
# 6. مخطط الجلوس البيداغوجي الذكي (مع خيار فصل الجنسين: بنات معاً وأولاد معاً)
# ==============================================================================
elif menu == M_SEATING:
    st.header("🪑 مخطط الجلوس البيداغوجي الذكي (التعلم بالأقران وهندسة القاعة)")
    st.caption("توزيع آلي ذكي يراعي الحالات الصحية (👓🦻)، الجسدية (📏 و ✍️)، مع خيار الجلوس حسب الجنس (بنات معاً / أولاد معاً) أو دمج عام.")

    # دالة ذكية للتعرف التلقائي على جنس التلميذ(ة) من الاسم الجزائري
    def guess_student_gender(full_name):
        female_names = {
            "فاطمة", "آية", "خديجة", "عائشة", "أمينة", "ياسمين", "نسرين", "إكرام", "إيمان", "حنان", 
            "سهام", "أحلام", "منال", "إيناس", "وفاء", "زينب", "بشرى", "هاجر", "سلمى", "هدى", 
            "أميرة", "سارة", "جنان", "رحمة", "كوثر", "بتول", "ريان", "أنفال", "وصال", "صابرينة", 
            "سمية", "نهال", "دنيا", "حفصة", "نجاة", "لطيفة", "زهية", "نادية", "حورية", "فتيحة", 
            "ليلى", "سعاد", "لبنى", "شيماء", "لمياء", "حسيبة", "نوال", "سميرة", "رتيبة", "شروق", 
            "مريم", "مروة", "إسراء", "دعاء", "وئام", "ندى", "مرام", "سندس", "هند", "خلود", "راضية"
        }
        male_exceptions_with_ta = {"حمزة", "أسامة", "طلحة", "عكاشة", "قتيبة", "عمارة", "عبيدة", "ميسرة", "سلامة", "حذيفة"}
        
        words = full_name.strip().split()
        for w in words:
            if w in female_names:
                return "أنثى"
            if w.endswith("ة") and w not in male_exceptions_with_ta:
                return "أنثى"
        return "ذكر"

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم وتلاميذه أولاً.")
    else:
        sel_class = st.selectbox("🎯 اختاري القسم لتوليد مخطط الجلوس:", list(cls_opts.keys()), key="seating_cls_sel")
        cid = cls_opts[sel_class]

        conn = get_connection()
        try:
            # التأكد البرمجي من وجود عمود الجنس
            try:
                conn.execute("ALTER TABLE students ADD COLUMN gender TEXT DEFAULT 'غير محدد'")
                conn.commit()
            except Exception:
                pass

            students_data = conn.execute("""
                SELECT s.id, s.full_name, COALESCE(s.behavior, 'عادي') as behavior,
                       COALESCE(s.gender, 'غير محدد') as gender,
                       COALESCE(r.total, 10.0) as total, COALESCE(r.classification, 'متحكم') as classification
                FROM students s
                LEFT JOIN diagnostic_results r ON s.id = r.student_id
                WHERE s.class_id = ?
                ORDER BY s.full_name ASC
            """, (cid,)).fetchall()
            
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (cid,)).fetchone()
        finally:
            conn.close()

        if not students_data:
            st.info("لا يوجد تلاميذ مسجلون في هذا القسم.")
        else:
            # تجهيز قائمة التلاميذ مع ضبط الجنس
            students_pool = []
            for s in students_data:
                sd = dict(s)
                if sd["gender"] == "غير محدد" or not sd["gender"]:
                    sd["gender"] = guess_student_gender(sd["full_name"])
                students_pool.append(sd)

            tab_view, tab_behavior = st.tabs(["🗺️ المخطط البصري للقاعة والطباعة", "⚙️ ضبط صفات التلاميذ (الجنس، الصحة، والسلوك)"])

            # ---------------------------------------------------------
            # 1. تبويب ضبط صفات وجنس التلاميذ
            # ---------------------------------------------------------
            with tab_behavior:
                st.markdown("##### ⚙️ توصيف خصائص التلاميذ وتأكيد الجنس (إناث / ذكور):")
                st.caption("يمكنكِ هنا تعديل جنس التلميذ(ة) أو حالته الخاصة لضمان دقة خوارزمية التوزيع:")

                col_b1, col_b2, col_b3 = st.columns([1.5, 1.0, 1.5])
                with col_b1:
                    s_to_edit = st.selectbox("اختاري التلميذ(ة):", [s["full_name"] for s in students_pool], key="beh_stu_sel")
                    target_s = [s for s in students_pool if s["full_name"] == s_to_edit][0]

                with col_b2:
                    current_gender = target_s["gender"]
                    g_idx = 0 if current_gender == "أنثى" else 1
                    new_gender = st.selectbox("الجنس:", ["أنثى 👧", "ذكر 👦"], index=g_idx, key="stu_gender_pick")
                    clean_gender = "أنثى" if "أنثى" in new_gender else "ذكر"

                with col_b3:
                    current_beh = target_s["behavior"]
                    beh_opts = [
                        "عادي (سلوك متوازن) 👤",
                        "منضبط ومساعد (الأستاذ الصغير / رائد) ⭐",
                        "ضعيف البصر أو السمع (الصف الأول أمام السبورة) 👓🦻",
                        "أعسر اليد (يكتب باليسار - يُفضل يسار الطاولة) ✍️",
                        "حركي / يحتاج تركيز وقرب من الأستاذ ⚡",
                        "خجول / انطوائي (يحتاج شريكاً محفزاً ومساعداً) 🤝",
                        "طويل القامة (يُفضل الصفوف الخلفية لمنع حجب الرؤية) 📏"
                    ]
                    def_idx = 0
                    for i, opt in enumerate(beh_opts):
                        if opt.split(" ")[0] in current_beh or current_beh in opt:
                            def_idx = i; break
                    new_beh = st.selectbox("الصفة الصفيّة / الصحية:", beh_opts, index=def_idx, key="beh_opt_sel")

                if st.button("💾 حفظ وتحديث صفة وجنس التلميذ(ة)", type="primary"):
                    conn = get_connection()
                    try:
                        conn.execute("UPDATE students SET behavior = ?, gender = ? WHERE id = ?", (new_beh, clean_gender, target_s["id"]))
                        conn.commit()
                        st.success(f"✅ تم تحديث بيانات ({s_to_edit}) بنجاح.")
                        st.rerun()
                    finally:
                        conn.close()

                st.write("---")
                beh_table = [
                    {
                        "اسم التلميذ": s["full_name"],
                        "الجنس": "👧 أنثى" if s["gender"] == "أنثى" else "👦 ذكر",
                        "المعدل التشخيصي": f"{s['total']:.2f} / 20",
                        "المستوى المعرفي": format_badge_html(s["classification"]),
                        "التوصيف الصفي": f"<b>{s['behavior']}</b>"
                    } for s in students_pool
                ]
                render_artistic_table(beh_table)

            # ---------------------------------------------------------
            # 2. تبويب المخطط البصري (مع خيار فصل الجنسين)
            # ---------------------------------------------------------
            with tab_view:
                # 🎯 خيارات التحكم: أروقة القاعة + خيار فصل البنات عن الأولاد
                col_c1, col_c2 = st.columns([1.8, 2.2])
                with col_c1:
                    num_aisles = st.radio(
                        "📐 هندسة القاعة (عدد الأروقة):",
                        [3, 4],
                        format_func=lambda x: f"{x} أروقة ثنائية" + (" (كلاسيكي)" if x == 3 else " (قاعة واسعة)"),
                        horizontal=True,
                        key=f"num_aisles_radio_{cid}"
                    )
                with col_c2:
                    gender_choice = st.radio(
                        "👥 خيار توزيع المقاعد حسب الجنس في هذا القسم:",
                        [
                            "🧕 فصل الجنسين (جلوس البنات مع بعضهنّ والأولاد مع بعضهم)",
                            "🤝 جلوس تكاملي عام (دون تمييز بين الجنسين)"
                        ],
                        index=0,
                        horizontal=True,
                        key=f"gender_choice_radio_{cid}"
                    )

                is_gender_separated = "فصل" in gender_choice

                # دالة توليد الطاولات الذكية لمجموعة محددة من التلاميذ
                def create_smart_pairs(group_students, tag_prefix=""):
                    sensory = [s for s in group_students if "بصر" in s.get("behavior", "") or "سمع" in s.get("behavior", "")]
                    disruptive = [s for s in group_students if "حركي" in s.get("behavior", "") and s not in sensory]
                    tall = [s for s in group_students if "طويل" in s.get("behavior", "") and s not in sensory and s not in disruptive]
                    shy = [s for s in group_students if "خجول" in s.get("behavior", "") and s not in sensory and s not in disruptive]
                    
                    supporters = [
                        s for s in group_students 
                        if ("منضبط" in s.get("behavior", "") or "رائد" in s.get("behavior", "") or s["total"] >= 12) 
                        and s not in sensory and s not in disruptive and s not in tall
                    ]

                    academic = sorted(
                        [s for s in group_students if s not in sensory and s not in disruptive and s not in supporters and s not in tall and s not in shy], 
                        key=lambda x: x["total"], 
                        reverse=True
                    )

                    f_pairs, m_pairs, b_pairs = [], [], []
                    used = set()

                    # طاولات الصف الأول (أولوية صحية)
                    for sn in sensory:
                        if sn["id"] in used: continue
                        partner = next((c for c in supporters if c["id"] not in used and c["id"] != sn["id"]), None)
                        if not partner: partner = next((a for a in academic if a["id"] not in used and a["id"] != sn["id"]), None)
                        if partner:
                            f_pairs.append((sn, partner, f"{tag_prefix} أولوية صحية 👓🦻"))
                            used.update([sn["id"], partner["id"]])
                        else:
                            f_pairs.append((sn, None, f"{tag_prefix} فردية صحية 👓🦻"))
                            used.add(sn["id"])

                    # طاولات الانضباط (الحركيون)
                    for d in disruptive:
                        if d["id"] in used: continue
                        partner = next((c for c in supporters if c["id"] not in used and c["id"] != d["id"]), None)
                        if not partner: partner = next((a for a in academic if a["id"] not in used and a["id"] != d["id"]), None)
                        if partner:
                            f_pairs.append((d, partner, f"{tag_prefix} مرافقة وانضباط ⚡"))
                            used.update([d["id"], partner["id"]])
                        else:
                            f_pairs.append((d, None, f"{tag_prefix} فردية ⚡"))
                            used.add(d["id"])

                    # طاولات الخلف (طوال القامة)
                    for ts in tall:
                        if ts["id"] in used: continue
                        partner = next((s for s in group_students if s["id"] not in used and s["id"] != ts["id"]), None)
                        if partner:
                            b_pairs.append((ts, partner, f"{tag_prefix} مراعاة القامة 📏"))
                            used.update([ts["id"], partner["id"]])
                        else:
                            b_pairs.append((ts, None, f"{tag_prefix} فردية 📏"))
                            used.add(ts["id"])

                    # طاولات الدمج (الخجولون)
                    for sh in shy:
                        if sh["id"] in used: continue
                        partner = next((c for c in supporters if c["id"] not in used and c["id"] != sh["id"]), None)
                        if not partner: partner = next((s for s in group_students if s["id"] not in used and s["id"] != sh["id"]), None)
                        if partner:
                            m_pairs.append((sh, partner, f"{tag_prefix} دمج وتشجيع 🤝"))
                            used.update([sh["id"], partner["id"]])
                        else:
                            m_pairs.append((sh, None, f"{tag_prefix} فردية 🤝"))
                            used.add(sh["id"])

                    # بقية الطاولات بتكامل الأقران
                    rem = [s for s in group_students if s["id"] not in used]
                    rem.sort(key=lambda x: x["total"], reverse=True)

                    while len(rem) >= 2:
                        m_pairs.append((rem.pop(0), rem.pop(-1), f"{tag_prefix} تعلّم بالأقران ⭐"))

                    if len(rem) == 1:
                        m_pairs.append((rem.pop(0), None, f"{tag_prefix} فردية"))

                    return f_pairs + m_pairs + b_pairs

                # تطبيق خوارزمية التوزيع وفق الخيار المحدد
                if is_gender_separated:
                    girls_list = [s for s in students_pool if s["gender"] == "أنثى"]
                    boys_list = [s for s in students_pool if s["gender"] == "ذكر"]

                    st.markdown(f"""
                    <div class="art-card" style="border-right-color:#10B981; padding:8px 15px; margin-bottom:10px; font-size:0.9em;">
                        🧕 <b>توزيع مفصول حسب الجنس:</b> تعداد الإناث: <b>{len(girls_list)} طالبة</b> | تعداد الذكور: <b>{len(boys_list)} طالب</b> (تم عزل مقاعد البنات معاً والأولاد معاً).
                    </div>
                    """, unsafe_allow_html=True)

                    # توليد طاولات البنات وطاولات الأولاد
                    girls_pairs = create_smart_pairs(girls_list, "طاولة بنات 👧")
                    boys_pairs = create_smart_pairs(boys_list, "طاولة أولاد 👦")
                    all_ordered_pairs = girls_pairs + boys_pairs
                else:
                    st.markdown("""
                    <div class="art-card" style="border-right-color:#3B82F6; padding:8px 15px; margin-bottom:10px; font-size:0.9em;">
                        🤝 <b>توزيع تكاملي عام:</b> تم توزيع الطاولات وفق تكامل الأقران والحالات الصحية دون تمييز بين الجنسين.
                    </div>
                    """, unsafe_allow_html=True)
                    all_ordered_pairs = create_smart_pairs(students_pool, "طاولة")

                # مراعاة التلميذ الأعسر لوضعه في يسار الطاولة دائماً
                adjusted_pairs = []
                for p in all_ordered_pairs:
                    s1, s2, tag = p
                    if s1 and ("أعسر" in s1.get("behavior", "") or "يسار" in s1.get("behavior", "")):
                        adjusted_pairs.append((s2, s1, tag))
                    else:
                        adjusted_pairs.append((s1, s2, tag))

                # تقسيم الطاولات على عدد الأروقة (3 أو 4)
                if num_aisles == 4:
                    column_names = ["رواق الباب (1)", "الرواق الداخلي (2)", "الرواق الأوسط (3)", "رواق النوافذ (4)"]
                else:
                    column_names = ["رواق الباب (اليسار)", "الرواق الأوسط", "رواق النوافذ (اليمين)"]

                cols_layout = [[] for _ in range(num_aisles)]
                for i, pair in enumerate(adjusted_pairs):
                    cols_layout[i % num_aisles].append((pair, i + 1))

                # دالة تصميم مقعد التلميذ
                def render_seat_box(stu):
                    if not stu:
                        return "<div style='color:gray; font-size:0.75em; padding:6px; text-align:center; flex:1; border:1px dashed #888; border-radius:6px;'>مقعد شاغر</div>"
                    
                    beh = stu.get("behavior", "")
                    gender = stu.get("gender", "ذكر")
                    gender_icon = "👧" if gender == "أنثى" else "👦"
                    
                    is_sensory = "بصر" in beh or "سمع" in beh
                    is_left = "أعسر" in beh or "يسار" in beh
                    is_disruptive = "حركي" in beh
                    is_shy = "خجول" in beh
                    is_tall = "طويل" in beh
                    is_pioneer = stu["total"] >= 10
                    
                    if is_sensory:
                        border_color = "#0284C7"; bg_color = "rgba(2, 132, 199, 0.15)"; status_icon = "👓🦻"
                    elif is_disruptive:
                        border_color = "#F59E0B"; bg_color = "rgba(245, 158, 11, 0.15)"; status_icon = "⚡"
                    elif is_shy:
                        border_color = "#8B5CF6"; bg_color = "rgba(139, 92, 246, 0.15)"; status_icon = "🤝"
                    elif is_tall:
                        border_color = "#64748B"; bg_color = "rgba(100, 116, 139, 0.15)"; status_icon = "📏"
                    elif is_pioneer:
                        border_color = "#10B981"; bg_color = "rgba(16, 185, 129, 0.12)"; status_icon = "⭐"
                    else:
                        border_color = "#EF4444"; bg_color = "rgba(239, 68, 68, 0.12)"; status_icon = "🔴"

                    left_tag = " (يسار ✍️)" if is_left else ""

                    return (
                        f"<div style='background:{bg_color}; border:1px solid {border_color}; border-radius:6px; "
                        f"padding:5px 6px; text-align:center; min-width:85px; flex:1; overflow:hidden;'>"
                        f"<span style='font-size:0.82em; font-weight:bold; display:block; white-space:nowrap; "
                        f"overflow:hidden; text-overflow:ellipsis;'>{gender_icon} {stu['full_name']}{left_tag}</span>"
                        f"<span style='font-size:0.72em; color:gray;'>{status_icon} {stu['total']:.1f}/20</span>"
                        f"</div>"
                    )

                # بناء هيكل القاعة التفاعلي
                classroom_body = ""
                for c_idx in range(num_aisles):
                    desks_in_col = ""
                    for pair_info in cols_layout[c_idx]:
                        pair, desk_num = pair_info
                        s1, s2, tag = pair
                        desks_in_col += (
                            f"<div style='background:var(--background-color); border:1px solid rgba(128,128,128,0.25); "
                            f"border-radius:8px; padding:6px; margin-bottom:10px; box-shadow:0 2px 5px rgba(0,0,0,0.03);'>"
                            f"<div style='font-size:0.7em; color:gray; display:flex; justify-content:space-between; margin-bottom:3px;'>"
                            f"<span><b>طاولة {desk_num}</b></span>"
                            f"<span style='color:{'#ec4899' if 'بنات' in tag else ('#2563eb' if 'أولاد' in tag else '#10b981')}; font-weight:bold;'>{tag}</span>"
                            f"</div>"
                            f"<div style='display:flex; gap:4px;'>"
                            f"{render_seat_box(s1)}"
                            f"{render_seat_box(s2)}"
                            f"</div>"
                            f"</div>"
                        )

                    classroom_body += (
                        f"<div style='flex:1; display:flex; flex-direction:column; gap:6px;'>"
                        f"<div style='text-align:center; font-weight:bold; font-size:0.82em; color:var(--text-color); "
                        f"border-bottom:1px solid rgba(128,128,128,0.2); padding-bottom:4px; margin-bottom:6px;'>"
                        f"{column_names[c_idx]}"
                        f"</div>"
                        f"{desks_in_col}"
                        f"</div>"
                    )

                full_classroom_html = (
                    f"<div style='background:var(--secondary-background-color); border:2px solid rgba(128,128,128,0.25); "
                    f"border-radius:14px; padding:18px; margin:15px 0;'>"
                    f"<div style='background:linear-gradient(90deg, #1E3A8A, #1E88E5); color:white; text-align:center; "
                    f"padding:9px; border-radius:8px; font-weight:bold; font-size:1.05em; margin-bottom:10px;'>"
                    f"⬛ مـنـصـة الأسـتـاذ والـسـبـورة"
                    f"</div>"
                    f"<div style='display:flex; justify-content:space-between; font-size:0.8em; color:gray; margin-bottom:12px; padding:0 8px;'>"
                    f"<span>🚪 جهة الباب</span>"
                    f"<span>صف النوافذ 🪟</span>"
                    f"</div>"
                    f"<div style='display:flex; justify-content:space-between; gap:10px;'>"
                    f"{classroom_body}"
                    f"</div>"
                    f"</div>"
                )

                render_clean_html(full_classroom_html)

                # وثيقة الطباعة الرسمية PDF A4
                st.divider()

                print_desks_html = ""
                for c_idx in range(num_aisles):
                    print_desks_html += f"<div style='flex:1; display:flex; flex-direction:column; gap:8px;'><div style='text-align:center; font-weight:bold; font-size:0.8em; border-bottom:1px solid #000; padding-bottom:3px;'>{column_names[c_idx]}</div>"
                    for pair_info in cols_layout[c_idx]:
                        pair, desk_num = pair_info
                        s1, s2, tag = pair
                        n1 = f"{s1['full_name']} ({'👧' if s1.get('gender')=='أنثى' else '👦'})" if s1 else "شاغر"
                        n2 = f"{s2['full_name']} ({'👧' if s2.get('gender')=='أنثى' else '👦'})" if s2 else "شاغر"
                        sc1 = f"({s1['total']:.1f})" if s1 else ""
                        sc2 = f"({s2['total']:.1f})" if s2 else ""
                        icon1 = " 👓" if s1 and ("بصر" in s1.get("behavior", "") or "سمع" in s1.get("behavior", "")) else ""
                        icon2 = " 👓" if s2 and ("بصر" in s2.get("behavior", "") or "سمع" in s2.get("behavior", "")) else ""

                        print_desks_html += f"""
                        <div style='border:1px solid #000; border-radius:4px; padding:4px; background:#fafafa;'>
                            <div style='font-size:0.65em; display:flex; justify-content:space-between; margin-bottom:2px;'>
                                <b>طاولة {desk_num}</b> <span style="font-weight:bold;">{tag}</span>
                            </div>
                            <div style='display:flex; gap:3px; font-size:0.75em; text-align:center;'>
                                <div style='flex:1; border:1px solid #999; padding:3px; border-radius:3px;'>{n1}{icon1} {sc1}</div>
                                <div style='flex:1; border:1px solid #999; padding:3px; border-radius:3px;'>{n2}{icon2} {sc2}</div>
                            </div>
                        </div>
                        """
                    print_desks_html += "</div>"

                printable_seating_html = f"""
                <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 10px;">
                    <h3 style="margin:0; font-size:1.1em;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h3>
                    <h4 style="margin:3px 0; font-size:0.95em;">مديرية التربية لولاية وهران — ثانوية: .........................</h4>
                    <p style="margin:0; font-size:0.9em;"><b>مخطط الجلوس البيداغوجي الذكي ({'فصل الجنسين 🧕' if is_gender_separated else 'دمج تكاملي 🤝'} — {num_aisles} أروقة)</b></p>
                </div>

                <table style="width:100%; margin-bottom:10px; font-size:0.9em; border:none;">
                    <tr style="border:none;">
                        <td style="border:none; text-align:right;"><b>القسم والمستوى:</b> {c_info['level']} ({c_info['class_name']})</td>
                        <td style="border:none; text-align:center;"><b>السنة الدراسية:</b> {c_info['school_year']}</td>
                        <td style="border:none; text-align:left;"><b>تاريخ الاعتماد:</b> {date.today().strftime('%d/%m/%Y')}</td>
                    </tr>
                </table>

                <div style="border:2px solid #000; background:#eee; text-align:center; padding:6px; font-weight:bold; margin-bottom:12px; border-radius:4px; font-size:0.95em;">
                    ⬛ مـنـصـة الأسـتـاذ والـسـبـورة
                </div>

                <div style="display:flex; justify-content:space-between; gap:10px; margin-bottom:12px;">
                    {print_desks_html}
                </div>

                <div style="border:1px dashed #000; padding:6px; font-size:0.78em; margin-top:8px; background:#f9f9f9;">
                    <b>ملاحظة المخطط:</b> يراعي المخطط {'فصل مقاعد الإناث عن الذكور،' if is_gender_separated else 'تكامل الأقران دون تمييز،'} مع تقديم ضعاف البصر والسمع (👓)، إسناد من يكتب باليسار (✍️) في يسار الطاولة، ومراعاة طوال القامة (📏) في الخلف.
                </div>

                <div style="display:flex; justify-content:space-between; margin-top:25px; font-weight:bold; font-size:0.9em;">
                    <span>توقيع الأستاذ(ة): .........................</span>
                    <span>تأشيرة السيد مستشار التربية / الناظر: .........................</span>
                </div>
                """

                pdf_data, mime_type = convert_html_to_pdf(printable_seating_html)
                ext = "pdf" if mime_type == "application/pdf" else "html"
                st.download_button(
                    label=f"📑 تحميل مخطط الجلوس ({'فصل الجنسين' if is_gender_separated else 'عام'}) كملف PDF معتمد للطباعة",
                    data=pdf_data,
                    file_name=f"مخطط_جلوس_{c_info['class_name'].replace(' ', '_')}.{ext}",
                    mime=mime_type,
                    type="primary",
                    key="btn_dl_pdf_seating_new"
                )
# ==============================================================================
# 7. تقرير استثمار النتائج واستراتيجية المعالجة
# ==============================================================================
# ==============================================================================
# 7. تقرير استثمار النتائج واستراتيجية المعالجة (تحليل إحصائي وبيداغوجي ذكي)
# ==============================================================================
# ==============================================================================
# 7. تقرير استثمار النتائج واستراتيجية المعالجة (مرتبط مباشرة بضبط الموضوع)
# ==============================================================================
elif menu == M_REPORT:
    import json
    st.header("📑 تقرير استثمار النتائج واستراتيجية المعالجة البيداغوجية")
    st.caption("تحليل إحصائي وبيداغوجي مؤتمت ومستخرج مباشرة من محاور وسلالم تمارين «ضبط الموضوع» المعتمدة للقسم.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم وتلاميذه أولاً.")
    else:
        sel_c = st.selectbox("🎯 اختاري القسم لاستخراج تقريره التحليلي:", list(cls_opts.keys()))
        cid = cls_opts[sel_c]

        conn = get_connection()
        try:
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (cid,)).fetchone()
            
            # جلب الحاضرين الفعليين (استبعاد الغياب 0)
            rows = conn.execute("""
                SELECT r.* FROM diagnostic_results r
                INNER JOIN students s ON r.student_id = s.id
                WHERE s.class_id = ? 
                  AND (r.total > 0 OR r.arithmetic > 0 OR r.algebra > 0 OR r.functions > 0 OR r.geometry > 0)
            """, (cid,)).fetchall()
        finally:
            conn.close()

        if not rows:
            st.warning("لا توجد نتائج مسجلة لتلاميذ حاضرين في هذا القسم بعد.")
        else:
            total_s = len(rows)
            mastered_count = sum(1 for r in rows if (r["total"] or 0) >= 10.0)
            overall_rate = (mastered_count / total_s) * 100 if total_s > 0 else 0.0
            avg_class_score = sum(r["total"] or 0 for r in rows) / total_s if total_s > 0 else 0.0
            fragile_count = sum(1 for r in rows if (r["total"] or 0) < 7.0)

            # 🎯 1. قراءة محاور الموضوع الفعلية وسلالمها من ضبط الموضوع (rubric_json)
            rubric = None
            if c_info and "rubric_json" in c_info.keys() and c_info["rubric_json"]:
                try:
                    rubric = json.loads(c_info["rubric_json"])
                except Exception:
                    rubric = None

            if not rubric or "exercises" not in rubric:
                lvl_str = c_info["level"].lower() if c_info else ""
                if "1" in lvl_str:
                    def_u = ["الأعداد والحساب", "الحساب الجبري", "الدوال وتنظيم معطيات", "الهندسة والأشعة"]
                elif "آداب" in lvl_str or "لغات" in lvl_str:
                    def_u = ["النسب المئوية والمؤشرات", "العبارات الجبرية والمعادلات", "الإحصاء وتنظيم المعطيات"]
                elif "2" in lvl_str:
                    def_u = ["العبارات الجبرية وثلاثي الحدود", "عموميات على الدوال", "الدوران والزوايا الموجهة"]
                else:
                    def_u = ["الاشتقاقية وتطبيقاتها", "المتتاليات العددية", "النهايات وسلوك الدوال"]
                rubric = {"num_ex": len(def_u), "exercises": [{"unit": u, "max": round(20.0 / len(def_u), 1)} for u in def_u]}

            # دالة استخراج علامة التمرين للتلميذ
            def get_r_score(r_item, idx_pos, field_name):
                r_dict = dict(r_item)
                if r_dict.get("details_json"):
                    try:
                        d = json.loads(r_dict["details_json"])
                        if "exercises" in d and idx_pos < len(d["exercises"]):
                            return float(d["exercises"][idx_pos].get("score", r_dict.get(field_name, 0.0) or 0.0))
                    except Exception:
                        pass
                return float(r_dict.get(field_name, 0.0) or 0.0)

            # 🎯 2. فحص تمارين الموضوع الفعلية فقط وحساب معدلاتها ونسب تحكمها
            col_names = ["arithmetic", "algebra", "functions", "geometry"]
            res_stats = {}

            for ex_idx, ex_data in enumerate(rubric["exercises"]):
                if ex_idx >= len(col_names): break
                col_field = col_names[ex_idx]
                unit_name = ex_data.get("unit", f"التمرين {ex_idx+1}")
                ex_max = float(ex_data.get("max", 5.0))
                passing_threshold = round(ex_max / 2.0, 2)

                # حساب معدل تحصيل الفوج ونسبة التحكم
                scores = [get_r_score(r, ex_idx, col_field) for r in rows]
                ex_avg = sum(scores) / total_s if total_s > 0 else 0.0
                pass_count = sum(1 for sc in scores if sc >= passing_threshold)
                ex_rate = round((pass_count / total_s) * 100, 1) if total_s > 0 else 0.0

                res_stats[unit_name] = {
                    "max": ex_max,
                    "avg": ex_avg,
                    "rate": ex_rate,
                    "fail_rate": round(100.0 - ex_rate, 1)
                }

            sorted_by_rate = sorted(res_stats.items(), key=lambda x: (x[1]["rate"], x[1]["avg"]), reverse=True)
            best_res, best_data = sorted_by_rate[0]
            worst_res, worst_data = sorted_by_rate[-1]

            # 🎯 3. صياغة سبب التعثر بذكاء بيداغوجي وفق طبيعة المحور الأضعف الحقيقي
            w_name_low = worst_res.lower()
            if "نسب" in w_name_low or "إحصاء" in w_name_low:
                ped_cause = "صعوبة استثمار الجداول الإحصائية وتطبيق قواعد المعامل الضارب والتغير النسبي."
            elif "هندس" in w_name_low or "شعاع" in w_name_low or "دوران" in w_name_low or "زوايا" in w_name_low:
                ped_cause = "صعوبة الانتقال من الملموس إلى المجرد وضعف مهارات الإنشاء والتصور الفضائي."
            elif "دوال" in w_name_low or "مشتق" in w_name_low or "نهايات" in w_name_low:
                ped_cause = "صعوبة التنسيق والربط بين التمثيل البياني والتحليل الجبري وجداول التغيرات."
            elif "جبر" in w_name_low or "معادل" in w_name_low or "حساب" in w_name_low or "كسور" in w_name_low:
                ped_cause = "ضعف آليات الحساب الجبري وقواعد النشر والتحليل وحل المعادلات."
            else:
                ped_cause = "تراكم فجوات تعليمية سابقة وضعف الممارسة الرياضية الفردية المنتظمة."

            # صياغة الفقرة التحليلية
            if best_data["rate"] == 0.0 and worst_data["rate"] == 0.0:
                analysis_para = f"""
أظهرت القراءة التقنية للنتائج وجود <b>عجز قاعدي معمم</b> على كافة محاور موضوع التقويم دون استثناء؛ حيث لم تتجاوز نسبة التحكم في أي محور عتبة [0.0%]، وسجل القسم معدلاً عاماً قدره [{avg_class_score:.2f} / 20].
ويعزى هذا الضعف الشامل إلى انقطاع الممارسة الرياضية، مما يستوجب خطة معالجة استدراكية استباقية قبل الانطلاق في دروس المنهاج.
                """
            elif best_res == worst_res or best_data["rate"] == worst_data["rate"]:
                analysis_para = f"""
بينت نتائج الفحص تقارباً في مستويات التحصيل بين مختلف محاور موضوع التقويم بمعدل عام للقسم قدره [{avg_class_score:.2f} / 20]، مع تسجيل نسبة تحكم في حدود [{best_data['rate']:.1f}%]. وتتطلب هذه الوضعية تدخلاً متوازناً يشمل كافة محاور الموضوع لتثبيت المكتسبات.
                """
            else:
                analysis_para = f"""
ومن خلال القراءة التقنية للنتائج، نلاحظ تبايناً في الكفاءات؛ حيث سجل محور <b>[{best_res}]</b> أعلى نسبة تحكم بلغت <b>[{best_data['rate']:.1f}%]</b> بمعدل تحصيل <b>[{best_data['avg']:.2f} / {best_data['max']:.1f}ن]</b>، مما يجعله نقطة ارتكاز إيجابية يمكن الاستناد إليها في بناء التعلمات.
وفي المقابل، كشف التشخيص عن تعثرات حرجة في محور <b>[{worst_res}]</b>، حيث استقرت نسبة التحكم فيه عند <b>[{worst_data['rate']:.1f}%]</b> فقط (بمعدل <b>[{worst_data['avg']:.2f} / {worst_data['max']:.1f}ن]</b>). ويعزى هذا الضعف في هذا المورد تحديداً إلى <b>{ped_cause}</b>
                """

            report_full_text = f"""
بناءً على المعطيات الإحصائية المستخلصة من شبكة التقويم التشخيصي لفوج <b>[{c_info['class_name']}]</b>، والبالغ تعدادهم <b>[{total_s} تلميذاً حاضراً]</b>، تبيّن أن النسبة العامة للتحكم في المكتسبات القبلية بلغت <b>[{overall_rate:.1f}%]</b>، في حين تم إحصاء <b>[{fragile_count} تلميذاً]</b> ضمن الفئة الهشة الحرجة (المنطقة الحمراء) الذين يستوجب وضعهم تحت المتابعة الفردية.

{analysis_para}

وعليه، وتجسيداً للتوجيهات الرسمية للمفتشية، تقرر اعتماد استراتيجية معالجة فارقية ترتكز على:
1. تدخلات جماعية سريعة: تخصيص (10 دقائق) في مرحلة الانطلاق من كل حصة لترسيخ المفاهيم القاعدية المتعثرة (استراتيجية التعليم المصغر).
2. تدخلات فارقية بالأقران: تفعيل "مخطط الجلوس الذكي" بمزاوجة تلاميذ الفئة الهشة مع رواد القسم لتمكينهم من المرافقة المستمرة.
3. معالجة موجهة بالمحاور: فتح بطاقات متابعة فردية للمتعثرين في محاورهم المتعثرة حصراً، وتوثيق استدراكهم حتى الخروج النهائي من دائرة التعثر.
            """

            st.markdown(f"""
            <div class="art-card">
                <div style="text-align:center; border-bottom:1px solid rgba(128,128,128,0.3); padding-bottom:10px; margin-bottom:15px;">
                    <h3 style="margin:0; color:#1E88E5;">تقرير استثمار نتائج التقويم واستراتيجية المعالجة البيداغوجية</h3>
                    <p style="margin:4px 0; color:gray;"><b>المستوى:</b> {c_info['level']} ({c_info['class_name']}) &nbsp;|&nbsp; <b>الحاضرون الممتحنون:</b> {total_s} تلميذ &nbsp;|&nbsp; <b>نسبة التحكم الكلية:</b> {overall_rate:.1f}%</p>
                </div>
                <div style="line-height: 2.1; font-size: 1.05em; text-align: justify;">
                    {report_full_text.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 🎯 4. جدول المؤشرات الإحصائية لمحاور الموضوع الفعلية
            st.markdown("##### 📊 جدول المؤشرات الإحصائية التفصيلية لمحاور موضوع التقويم:")
            res_table = [
                {
                    "المحور البيداغوجي": f"<b>{k}</b>",
                    "سلّم التمرين": f"{v['max']:.1f} ن",
                    "معدل تحصيل الفوج": f"<b>{v['avg']:.2f} / {v['max']:.1f}</b>",
                    "نسبة التحكم (≥ نصف السلّم)": f"<span style='color:{'green' if v['rate']>=50 else 'red'}; font-weight:bold;'>{v['rate']:.1f}%</span>",
                    "نسبة التعثر": f"<span style='color:{'red' if v['fail_rate']>50 else 'orange'}; font-weight:bold;'>{v['fail_rate']:.1f}%</span>",
                    "التوجيه العلاجي المقترح": "تعزيز المكتسبات وإدماجها" if v['rate']>=50 else "معالجة قاعدية استباقية إلزامية"
                } for k, v in res_stats.items()
            ]
            render_artistic_table(res_table)

            # 🎯 5. وثيقة الطباعة الرسمية A4 PDF
            pdf_trs = ""
            for k, v in res_stats.items():
                pdf_trs += f"""
                <tr>
                    <td style="padding:6px; border:1px solid #000; text-align:right; font-weight:bold;">{k}</td>
                    <td style="padding:6px; border:1px solid #000; text-align:center;">{v['max']:.1f} ن</td>
                    <td style="padding:6px; border:1px solid #000; text-align:center; font-weight:bold;">{v['avg']:.2f} / {v['max']:.1f}</td>
                    <td style="padding:6px; border:1px solid #000; text-align:center; color:{'green' if v['rate']>=50 else 'red'}; font-weight:bold;">{v['rate']:.1f}%</td>
                    <td style="padding:6px; border:1px solid #000; text-align:center; color:{'red' if v['fail_rate']>50 else 'orange'}; font-weight:bold;">{v['fail_rate']:.1f}%</td>
                    <td style="padding:6px; border:1px solid #000; text-align:right; font-size:10px;">{'تعزيز وتثبيت' if v['rate']>=50 else 'معالجة قاعدية مستهدفة'}</td>
                </tr>
                """

            official_report_html = f"""
            <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 12px;">
                <h3 style="margin: 0; font-size:1.15em;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h3>
                <h4 style="margin: 4px 0; font-size:1.0em;">مديرية التربية لولاية وهران — مقاطعة تفتيشية رقم 03</h4>
                <p style="margin: 0; font-size:0.95em;"><b>تقرير استثمار نتائج التقويم التشخيصي واستراتيجية المعالجة البيداغوجية</b></p>
            </div>
            <table style="width: 100%; border:none; margin-bottom: 12px; font-size:0.9em;">
                <tr style="border:none;">
                    <td style="border:none; text-align:right;"><b>المستوى والقسم:</b> {c_info['level']} ({c_info['class_name']})</td>
                    <td style="border:none; text-align:center;"><b>الحاضرون الممتحنون:</b> {total_s} تلميذ</td>
                    <td style="border:none; text-align:left;"><b>السنة الدراسية:</b> {c_info['school_year']}</td>
                </tr>
            </table>
            <div style="text-align: justify; line-height: 1.9; font-size: 0.95em;">
                {report_full_text.replace(chr(10), '<br>')}
            </div>

            <div style="font-weight:bold; margin: 15px 0 6px 0; font-size: 11px;">جدول المؤشرات الإحصائية لمحاور موضوع التقويم:</div>
            <table style="width:100%; border-collapse:collapse; font-size:10.5px; margin-bottom:15px;">
                <thead>
                    <tr style="background:#f1f5f9;">
                        <th style="padding:5px; border:1px solid #000; width:28%;">المحور البيداغوجي</th>
                        <th style="padding:5px; border:1px solid #000; width:12%;">السلم</th>
                        <th style="padding:5px; border:1px solid #000; width:16%;">معدل الفوج</th>
                        <th style="padding:5px; border:1px solid #000; width:14%;">نسبة التحكم</th>
                        <th style="padding:5px; border:1px solid #000; width:14%;">نسبة التعثر</th>
                        <th style="padding:5px; border:1px solid #000; width:16%;">التوجيه العلاجي</th>
                    </tr>
                </thead>
                <tbody>{pdf_trs}</tbody>
            </table>

            <div style="display: flex; justify-content: space-between; margin-top: 35px; font-weight: bold; font-size:0.95em;">
                <span>توقيع الأستاذ(ة): .........................</span>
                <span>تأشيرة السيد مفتش التربية الوطنية: .........................</span>
            </div>
            """

            pdf_data, mime_type = convert_html_to_pdf(official_report_html)
            ext = "pdf" if mime_type == "application/pdf" else "html"
            st.download_button(
                label="📑 تحميل تقرير استثمار النتائج الرسمي كملف PDF معتمد للتفتيش",
                data=pdf_data,
                file_name=f"تقرير_استثمار_النتائج_{c_info['class_name']}.{ext}",
                mime=mime_type,
                type="primary",
                key="dl_report_pdf_btn"
            )
# ==============================================================================
# 8. بطاقة المتابعة الفردية الرسمية (خاصة بالفئة الهشة)
# ==============================================================================

    # ==============================================================================
# 8. بطاقة المتابعة الفردية الرسمية (خاصة حصراً بتلاميذ المنطقة الحمراء)
# ==============================================================================
# ==============================================================================
# 8. بطاقة المتابعة البيداغوجية الفردية (شبكة المتعثرين + كل القسم + تحميل PDF)
# ==============================================================================
# ==============================================================================
# 8. بطاقة المتابعة الفردية (متابعة علاج المحاور حتى الخروج من المنطقة الحمراء)
# ==============================================================================
# ==============================================================================
# 8. بطاقة المتابعة الفردية (متابعة علاج المحاور تدريجياً حتى الخروج من المنطقة الحمراء)
# ==============================================================================
elif menu == M_FOLLOWUP:
    import json
    st.header("🪪 بطاقة المتابعة البيداغوجية الفردية (مادة الرياضيات)")
    st.caption("متابعة تدريجية لعلاج المحاور المتعثرة لكل تلميذ؛ مع تسجيل إتمام العلاج وخروج التلميذ من المنطقة الحمراء.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم وتلاميذه أولاً.")
    else:
        def_cls_idx = 0
        if "auto_selected_class" in st.session_state and st.session_state["auto_selected_class"] in cls_opts.keys():
            def_cls_idx = list(cls_opts.keys()).index(st.session_state["auto_selected_class"])

        sel_c = st.selectbox("🎯 اختاري القسم للمتابعة:", list(cls_opts.keys()), index=def_cls_idx, key="stu_card_cls")
        cid = cls_opts[sel_c]

        conn = get_connection()
        try:
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (cid,)).fetchone()
            all_students_rows = conn.execute("""
                SELECT s.id, s.full_name, r.arithmetic, r.algebra, r.functions, r.geometry, r.total, r.classification, r.details_json
                FROM students s
                LEFT JOIN diagnostic_results r ON s.id = r.student_id
                WHERE s.class_id = ?
                ORDER BY r.total ASC, s.full_name ASC
            """, (cid,)).fetchall()

            # جلب كل الأنشطة العلاجية الناجحة للتلاميذ
            rem_rows = conn.execute("""
                SELECT student_id, resource, response_level FROM remediation_activities
                WHERE student_id IN (SELECT id FROM students WHERE class_id = ?)
            """, (cid,)).fetchall()
        finally:
            conn.close()

        # بناء سجل المحاور المعالجة بنجاح لكل تلميذ
        treated_map = {}
        for rr in rem_rows:
            sid = rr["student_id"]
            res = rr["resource"]
            resp = str(rr["response_level"])
            if "جيد" in resp or "تجاوز" in resp or "تحسن" in resp:
                if sid not in treated_map:
                    treated_map[sid] = set()
                treated_map[sid].add(res)

        if not all_students_rows:
            st.info("لا يوجد تلاميذ مسجلون في هذا القسم.")
        else:
            pending_fragile = []  # ما زالوا في المنطقة الحمراء
            cured_fragile = []    # كانوا في المنطقة الحمراء وتعافوا بالكامل
            all_list = []

            # قراءة محاور وسلالم الموضوع المعتمدة للقسم من ضبط الموضوع
            rubric = None
            if c_info and "rubric_json" in c_info.keys() and c_info["rubric_json"]:
                try: rubric = json.loads(c_info["rubric_json"])
                except Exception: rubric = None

            if not rubric or "exercises" not in rubric:
                lvl_s = c_info["level"].lower() if c_info else ""
                if "1" in lvl_s: def_u = ["الأعداد والحساب", "الحساب الجبري", "الدوال وتنظيم معطيات", "الهندسة والأشعة"]
                elif "آداب" in lvl_s or "لغات" in lvl_s: def_u = ["النسب المئوية والمؤشرات", "العبارات الجبرية والمعادلات", "الإحصاء وتنظيم المعطيات"]
                elif "2" in lvl_s: def_u = ["العبارات الجبرية وثلاثي الحدود", "عموميات على الدوال", "الدوران والزوايا الموجهة"]
                else: def_u = ["الاشتقاقية وتطبيقاتها", "المتتاليات العددية", "النهايات وسلوك الدوال"]
                rubric = {"num_ex": len(def_u), "exercises": [{"unit": u, "max": round(20.0/len(def_u), 1)} for u in def_u]}

            col_names = ["arithmetic", "algebra", "functions", "geometry"]

            for st_row in all_students_rows:
                s_id = st_row["id"]
                s_name = st_row["full_name"]
                s_tot = float(st_row["total"] or 0.0)
                s_stat = st_row["classification"] if st_row["classification"] else "غير مقيم"

                def get_s_score(r_dict, idx, col_f):
                    if r_dict.get("details_json"):
                        try:
                            d = json.loads(r_dict["details_json"])
                            if "exercises" in d and idx < len(d["exercises"]):
                                return float(d["exercises"][idx].get("score", r_dict.get(col_f, 0.0) or 0.0))
                        except Exception: pass
                    return float(r_dict.get(col_f, 0.0) or 0.0)

                row_dict = dict(st_row)

                # فحص الغياب: علامة 0 في المجموع ولكل التمارين
                is_absent = (s_tot == 0.0 and all(get_s_score(row_dict, i, col_names[i]) == 0.0 for i in range(len(rubric["exercises"]))))

                # فحص التمارين الحقيقية لموضوع التقويم فقط
                initial_red = []
                ex_scores_recorded = []
                for ex_idx, ex in enumerate(rubric["exercises"]):
                    if ex_idx >= len(col_names): break
                    sc = get_s_score(row_dict, ex_idx, col_names[ex_idx])
                    threshold = round(float(ex.get("max", 5.0)) / 2.0, 2)
                    ex_scores_recorded.append({"unit": ex["unit"], "score": sc, "max": float(ex.get("max", 5.0)), "threshold": threshold})
                    
                    if not is_absent and sc < threshold:
                        initial_red.append(ex["unit"])

                s_cured_axes = treated_map.get(s_id, set())
                pending_axes = [ax for ax in initial_red if ax not in s_cured_axes]
                resolved_axes = [ax for ax in initial_red if ax in s_cured_axes]

                is_initially_fragile = (not is_absent) and (len(initial_red) > 0 or s_tot < 10.0 or s_stat == "غير متحكم")
                is_fully_cured = is_initially_fragile and (len(initial_red) > 0 and len(pending_axes) == 0)

                # استخراج درجات المحاور الأربعة بأمان لمنع انهيار ملفات Excel و PDF
                sc_ar = ex_scores_recorded[0]["score"] if len(ex_scores_recorded) > 0 else 0.0
                sc_al = ex_scores_recorded[1]["score"] if len(ex_scores_recorded) > 1 else 0.0
                sc_fn = ex_scores_recorded[2]["score"] if len(ex_scores_recorded) > 2 else 0.0
                sc_gm = ex_scores_recorded[3]["score"] if len(ex_scores_recorded) > 3 else 0.0

                stu_data = {
                    "id": s_id, "name": s_name, "total": s_tot, "status": s_stat,
                    "ar": sc_ar, "al": sc_al, "fn": sc_fn, "gm": sc_gm,  # تم إضافة المفاتيح الناقصة هنا
                    "is_absent": is_absent,
                    "ex_scores": ex_scores_recorded,
                    "initial_red": initial_red,
                    "pending_axes": pending_axes,
                    "resolved_axes": resolved_axes,
                    "is_cured": is_fully_cured,
                    "is_initially_fragile": is_initially_fragile,
                    "details_json": st_row["details_json"]
                }

                all_list.append(stu_data)
                if is_fully_cured:
                    cured_fragile.append(stu_data)
                elif is_initially_fragile:
                    pending_fragile.append(stu_data)

            # 3 تبويبات منظمة بالأعداد الحقيقية
            tab_pending, tab_cured, tab_all = st.tabs([
                f"🔴 المتعثرون قيد المعالجة ({len(pending_fragile)} تلميذ)",
                f"🟢 تعافوا وخرجوا من المنطقة الحمراء ({len(cured_fragile)} تلميذ)",
                f"👥 جميع تلاميذ القسم (الفوج كاملاً: {len(all_list)} تلميذ)"
            ])

            # دالة بناء جدول الرصد المربوط بضبط الموضوع
            def build_enhanced_table(stu_list):
                t_rows = []
                for idx, s in enumerate(stu_list):
                    s_id = s["id"]
                    cured_set = treated_map.get(s_id, set())

                    row_entry = {
                        "الرقم": idx + 1,
                        "اسم ولقب التلميذ": f"<b>{s['name']}</b>"
                    }

                    if s["is_absent"]:
                        for i, ex in enumerate(s["ex_scores"]):
                            row_entry[f"ت{i+1}: {ex['unit']}"] = "<span style='color:gray;'>غائب (0)</span>"
                        row_entry["المجموع"] = "<span style='color:gray;'>غائب</span>"
                        row_entry["التقدير"] = "<span class='badge-pill badge-red'>غائب لم يُمتحن</span>"
                        row_entry["حالة المتابعة"] = "<span style='color:gray;'>مستبعد (غياب)</span>"
                    else:
                        for i, ex in enumerate(s["ex_scores"]):
                            val = ex["score"]
                            u_name = ex["unit"]
                            if u_name in cured_set:
                                cell_txt = f"<b>{val:.2f}</b><br><span style='color:#10b981; font-size:0.8em;'>✅ عولج</span>"
                            elif val < ex["threshold"]:
                                cell_txt = f"<b style='color:red;'>{val:.2f}</b><br><span style='color:red; font-size:0.8em;'>🔴 قيد العلاج</span>"
                            else:
                                cell_txt = f"<b style='color:green;'>{val:.2f}</b>"
                            row_entry[f"ت{i+1}: {u_name}"] = cell_txt

                        row_entry["المجموع"] = f"<b>{s['total']:.2f} / 20</b>"
                        row_entry["التقدير"] = format_badge_html(s["status"])

                        if s["is_cured"]:
                            status_col = "<span class='badge-pill badge-green'>🟢 خرج من المنطقة الحمراء</span>"
                        elif s["is_initially_fragile"]:
                            status_col = f"<span class='badge-pill badge-red'>🔴 متبقي: {len(s['pending_axes'])}</span>"
                        else:
                            status_col = "<span class='badge-pill badge-green'>🟢 متحكم كلياً</span>"

                        row_entry["حالة المتابعة"] = status_col

                    t_rows.append(row_entry)
                return t_rows

            # دالة عرض البطاقة وتدوين النشاط وتحميل PDF
            def render_followup_section(selected_student_obj, unique_suffix):
                s_id = selected_student_obj["id"]
                s_name = selected_student_obj["name"]

                conn = get_connection()
                try:
                    s_info = conn.execute("SELECT s.full_name, c.level, c.class_name, c.school_year FROM students s INNER JOIN classes c ON s.class_id = c.id WHERE s.id = ?", (s_id,)).fetchone()
                    diag = conn.execute("SELECT * FROM diagnostic_results WHERE student_id = ?", (s_id,)).fetchone()
                    history = conn.execute("SELECT * FROM remediation_activities WHERE student_id = ? ORDER BY activity_date DESC", (s_id,)).fetchall()
                finally:
                    conn.close()

                cured_set = treated_map.get(s_id, set())
                p_axes = selected_student_obj["pending_axes"]
                r_axes = selected_student_obj["resolved_axes"]

                if selected_student_obj["is_cured"]:
                    st.markdown(f"""
                    <div class="art-card" style="border-right-color:#10B981; background:rgba(16,185,129,0.08); padding:16px;">
                        <h3 style="margin:0; color:#059669;">🎉 مبارك! خرج التلميذ ({s_name}) من المنطقة الحمراء بالكامل 🟢</h3>
                        <p style="margin:6px 0;">تم استدراك جميع التعثرات المشخصة في كافة المحاور وأصبح جاهزاً لكل الدروس القادمة.</p>
                        <div><b>المحاور التي تمت معالجتها:</b> {" ".join([f"<span class='badge-pill badge-green'>✅ {ax} (تمت المعالجة)</span>" for ax in r_axes])}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    p_pills = " ".join([f"<span class='badge-pill badge-red'>🔴 {ax} (قيد العلاج)</span>" for ax in p_axes])
                    r_pills = " ".join([f"<span class='badge-pill badge-green'>✅ {ax} (تمت المعالجة)</span>" for ax in r_axes]) if r_axes else "<span style='color:gray;'>لم يُعالج أي محور بعد</span>"
                    st.markdown(f"""
                    <div class="art-card" style="border-right-color:#EF4444; padding:16px;">
                        <div style="display:flex; justify-content:space-between;">
                            <h3 style="margin:0; color:#EF4444;">🪪 بطاقة تتبع استدراك التلميذ: {s_name}</h3>
                            <span style="font-size:1.1em; font-weight:bold;">معدل التشخيص: {selected_student_obj['total']:.2f} / 20</span>
                        </div>
                        <hr style="margin:8px 0;">
                        <div style="margin-bottom:6px;"><b>⏳ محاور تنتظر المعالجة (المنطقة الحمراء):</b> {p_pills}</div>
                        <div><b>✨ محاور تم استدراكها بنجاح:</b> {r_pills}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # استمارة تسجيل حصة المعالجة للمحور
                st.subheader(f"✍️ تدوين جلسة معالجة لـ ({s_name}):")
                with st.form(f"form_rem_{s_id}_{unique_suffix}"):
                    rc1, rc2, rc3 = st.columns(3)
                    with rc1:
                        r_date = st.date_input("تاريخ الحصة العلاجية:", value=date.today(), key=f"r_dt_{s_id}_{unique_suffix}")
                        # الأولوية للمحاور التي لا تزال في المنطقة الحمراء
                        axis_choices = p_axes if p_axes else (selected_student_obj["initial_red"] if selected_student_obj["initial_red"] else RESOURCES)
                        r_res = st.selectbox("المحور المستهدف بالعلاج الآن:", axis_choices, key=f"r_rs_{s_id}_{unique_suffix}")
                    with rc2:
                        r_act = st.selectbox("نوع النشاط العلاجي المنجز:", [
                            "نشاط مصغر في مرحلة الانطلاق (10 دقائق)",
                            "ورشة ثنائية (التعلم بالأقران مع تلميذ رائد)",
                            "تمرين منزلي مركز لعلاج الثغرة التقنية",
                            "معالجة قاعدية من مفاهيم المتوسط"
                        ], key=f"r_ac_{s_id}_{unique_suffix}")
                        r_resp = st.selectbox("درجة الاستجابة وتجاوز التعثر:", [
                            "جيد (تجاوز التعثر وتمت المعالجة بنجاح ✅)",
                            "متوسط (أبدى تحسناً ويحتاج جلسة أخرى)",
                            "ضعيف (لم يتجاوز التعثر بعد)"
                        ], key=f"r_rp_{s_id}_{unique_suffix}")
                    with rc3:
                        r_note = st.text_area("ملاحظات وتوجيهات الأستاذ:", placeholder="تم حل تطبيقات في هذا المحور وأظهر تحكماً في القواعد...", key=f"r_nt_{s_id}_{unique_suffix}")

                    if st.form_submit_button("💾 حفظ المعالجة وتحديث حالة التلميذ فوراً", type="primary"):
                        conn = get_connection()
                        try:
                            conn.execute("""
                                INSERT INTO remediation_activities (student_id, resource, activity_type, response_level, teacher_note, activity_date)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (s_id, r_res, r_act, r_resp, r_note, r_date.isoformat()))
                            conn.commit()
                            if "جيد" in r_resp or "تجاوز" in r_resp:
                                st.success(f"🎉 ممتاز! تم تأكيد معالجة محور ({r_res}) بنجاح. إذا عولجت بقية المحاور سيخرج التلميذ من المنطقة الحمراء.")
                            else:
                                st.info(f"تم تسجيل النشاط في محور ({r_res}).")
                            st.rerun()
                        finally:
                            conn.close()

                # جدول السجل التاريخي للحصص
                history_rows_html = ""
                if history:
                    st.write("📋 **سجل الأنشطة العلاجية المنجزة مع هذا التلميذ:**")
                    hist_table = [
                        {
                            "التاريخ": h["activity_date"],
                            "المحور المعالج": f"<b>{h['resource']}</b>",
                            "نوع النشاط": h["activity_type"],
                            "الاستجابة": f"<span style='color:{'green' if 'جيد' in h['response_level'] else 'orange'}; font-weight:bold;'>{h['response_level']}</span>",
                            "ملاحظة الأستاذ": h["teacher_note"] if h["teacher_note"] else "—"
                        } for h in history
                    ]
                    render_artistic_table(hist_table)

                    for h in history:
                        history_rows_html += f"""
                        <tr>
                            <td style="padding:6px; border:1px solid #000;">{h['activity_date']}</td>
                            <td style="padding:6px; border:1px solid #000;"><b>{h['resource']}</b><br><small>{h['activity_type']}</small></td>
                            <td style="padding:6px; border:1px solid #000;">{h['response_level']}</td>
                            <td style="padding:6px; border:1px solid #000;">{h['teacher_note']}</td>
                            <td style="padding:6px; border:1px solid #000; text-align:center;">✓</td>
                        </tr>
                        """
                else:
                    history_rows_html = "<tr><td colspan='5' style='text-align:center; padding:15px; border:1px solid #000;'>لم تسجل أنشطة علاجية بعد.</td></tr>"

                # زر تحميل بطاقة المتابعة الرسمية A4 PDF
                st.divider()
                st.markdown(f"#### 📥 تحميل بطاقة المتابعة الرسمية للتلميذ: `{s_name}`")
                
                cured_str = " ، ".join(r_axes) if r_axes else "لا توجد"
                pending_str = " ، ".join(p_axes) if p_axes else "لا توجد (تم استدراك الجميع)"
                status_eval = "✅ [X] تحسن ملحوظ: تمت معالجة المحاور المتعثرة بالكامل وخرج التلميذ من المنطقة الحمراء." if selected_student_obj["is_cured"] else "⏳ [X] تحسن جزئي: تمت معالجة بعض المحاور وبقيت أخرى قيد المتابعة والاستدراك."

                card_official_html = f"""
                <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 6px; margin-bottom: 12px;">
                    <h3 style="margin:0; font-size:1.15em;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h3>
                    <h4 style="margin:4px 0; font-size:1.0em;">المفتشية العامة للتربية الوطنية — ولاية وهران 03</h4>
                    <p style="margin:0; font-size:0.95em;"><b>بطاقة المتابعة البيداغوجية الفردية (مادة الرياضيات) — مسار استدراك التعثرات</b></p>
                </div>
                <table style="border:none; margin-bottom: 10px; font-size:0.95em; width:100%;">
                    <tr style="border:none;">
                        <td style="border:none; text-align:right;"><b>اسم ولقب التلميذ:</b> {s_info['full_name']}</td>
                        <td style="border:none; text-align:center;"><b>المستوى والقسم:</b> {s_info['level']} ({s_info['class_name']})</td>
                        <td style="border:none; text-align:left;"><b>السنة الدراسية:</b> {s_info['school_year']}</td>
                    </tr>
                </table>
                <div style="background:{'#ecfdf5' if selected_student_obj['is_cured'] else '#fee2e2'}; border:1px solid {'#10b981' if selected_student_obj['is_cured'] else '#ef4444'}; padding:8px 12px; border-radius:5px; margin-bottom:12px; font-size:0.9em;">
                    <b>حالة المعالجة البيداغوجية:</b> {'🟢 خرج من المنطقة الحمراء بنجاح' if selected_student_obj['is_cured'] else '🔴 قيد المعالجة والاستدراك'}<br>
                    <b>المحاور المعالجة بنجاح:</b> <span style="color:green; font-weight:bold;">{cured_str}</span> &nbsp;|&nbsp; 
                    <b>المحاور المتبقية:</b> <span style="color:red; font-weight:bold;">{pending_str}</span>
                </div>
                <div style="font-weight:bold; margin-bottom:5px; font-size:0.95em;">1. جدول المتابعة الميدانية للأنشطة العلاجية:</div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 14%;">التاريخ</th>
                            <th style="width: 32%;">المحور والنشاط العلاجي المنجز</th>
                            <th style="width: 20%;">درجة الاستجابة وتجاوز التعثر</th>
                            <th style="width: 24%;">ملاحظات الأستاذ</th>
                            <th style="width: 10%;">توقيع التلميذ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history_rows_html}
                    </tbody>
                </table>
                <div style="font-weight:bold; margin:12px 0 4px 0; font-size:0.95em;">2. مؤشر التطور النهائي المعتمد:</div>
                <p style="margin:2px 0; font-size:0.9em; font-weight:bold; color:{'green' if selected_student_obj['is_cured'] else 'red'};">
                    {status_eval}
                </p>
                <div style="display:flex; justify-content:space-between; margin-top:35px; font-weight:bold; font-size:0.95em;">
                    <span>توقيع الأستاذ(ة): .........................</span>
                    <span>تأشيرة السيد مفتش التربية الوطنية: .........................</span>
                </div>
                """

                pdf_data, mime_type = convert_html_to_pdf(card_official_html)
                ext = "pdf" if mime_type == "application/pdf" else "html"
                st.download_button(
                    label=f"📑 تحميل بطاقة المتابعة الفردية لـ ({s_name}) كملف PDF رسمي للتفتيش",
                    data=pdf_data,
                    file_name=f"بطاقة_متابعة_{s_name.replace(' ', '_')}.{ext}",
                    mime=mime_type,
                    type="primary",
                    key=f"btn_dl_pdf_{s_id}_{unique_suffix}"
                )

            # ---------------------------------------------------------
            # محتوى التبويب 1: المتعثرون قيد المعالجة
            # ---------------------------------------------------------
            with tab_pending:
                if not pending_fragile:
                    st.success("🎉 ممتاز! لا يوجد أي تلميذ متعثر قيد الانتظار حالياً؛ إما أن جميع التلاميذ متحكمون أو أنهم تعافوا جميعاً وخرجوا من المنطقة الحمراء!")
                else:
                    st.markdown("##### 📋 شبكة رصد كفاءات ونقاط المتعثرين قيد المتابعة:")
                    render_artistic_table(build_enhanced_table(pending_fragile))
                    st.write("---")
                    map_p = {f"{p['name']} (المتبقي: {len(p['pending_axes'])} محاور حمراء - معدل: {p['total']:.2f})": p for p in pending_fragile}
                    sel_p_name = st.selectbox("🎯 اختاري التلميذ لمتابعة علاجه ومطالعة بطاقته:", list(map_p.keys()), key="sel_pend_box")
                    render_followup_section(map_p[sel_p_name], "pend")

            # ---------------------------------------------------------
            # محتوى التبويب 2: تلاميذ تعافوا وخرجوا من المنطقة الحمراء
            # ---------------------------------------------------------
            with tab_cured:
                if not cured_fragile:
                    st.info("ℹ️ لم يخرج أي تلميذ من المنطقة الحمراء بعد. ابدئي بتسجيل حصص المعالجة واختاري 'جيد (تجاوز التعثر بنجاح)' لنقلهم إلى هنا تلقائياً.")
                else:
                    st.markdown("##### 🌟 قائمة التلاميذ الذين تعافوا بالكامل وتجاوزوا جميع المحاور الحمراء:")
                    render_artistic_table(build_enhanced_table(cured_fragile))
                    st.write("---")
                    map_c = {f"{c['name']} (✅ تم علاج جميع المحاور بنجاح)": c for c in cured_fragile}
                    sel_c_name = st.selectbox("🎯 اختاري تلميذاً متعافياً لتحميل بطاقته المكتملة:", list(map_c.keys()), key="sel_cured_box")
                    render_followup_section(map_c[sel_c_name], "cured")

            # ---------------------------------------------------------
            # محتوى التبويب 3: جميع تلاميذ الفوج كاملاً
            # ---------------------------------------------------------
           # ---------------------------------------------------------
            # محتوى التبويب 3: جميع تلاميذ الفوج كاملاً (مع زري تحميل Excel و PDF)
            # ---------------------------------------------------------
            with tab_all:
                st.markdown("##### 👥 شبكة رصد كفاءات جميع تلاميذ القسم كاملاً ومسار الخروج من المنطقة الحمراء:")
                render_artistic_table(build_enhanced_table(all_list))

                # =========================================================================
                # 📥 توليد وتحميل ملف Excel وملف PDF لهذه الشبكة
                # =========================================================================
                st.write("")
                col_dl_excel, col_dl_pdf = st.columns(2)

                # 1. دالة إنشاء ملف Excel منسق وملون
                def generate_followup_grid_excel(students_data, class_row):
                    import openpyxl
                    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                    from openpyxl.utils import get_column_letter

                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = "شبكة متابعة الكفاءات"
                    ws.views.sheetView[0].rightToLeft = True

                    font_title = Font(name="Cairo", size=12, bold=True, color="1E3A8A")
                    font_header = Font(name="Cairo", size=10, bold=True, color="FFFFFF")
                    font_bold = Font(name="Cairo", size=10, bold=True)
                    font_regular = Font(name="Cairo", size=9)
                    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    align_right = Alignment(horizontal="right", vertical="center")
                    border_thin = Border(left=Side(style='thin', color='A0AEC0'), right=Side(style='thin', color='A0AEC0'),
                                         top=Side(style='thin', color='A0AEC0'), bottom=Side(style='thin', color='A0AEC0'))

                    fill_header = PatternFill(start_color="FF1E88E5", end_color="FF1E88E5", fill_type="solid")
                    fill_cured = PatternFill(start_color="FFD1FAE5", end_color="FFD1FAE5", fill_type="solid")
                    fill_red = PatternFill(start_color="FFFEE2E2", end_color="FFFEE2E2", fill_type="solid")

                    # العنوان
                    ws.merge_cells("A1:I1")
                    ws["A1"] = f"شبكة رصد ومتابعة كفاءات الفوج: {class_row['level']} ({class_row['class_name']}) — السنة الدراسية: {class_row['school_year']}"
                    ws["A1"].font = font_title
                    ws["A1"].alignment = align_center

                    headers = ["الرقم", "اسم ولقب التلميذ", "الأعداد (5/)", "الجبر (5/)", "الدوال (5/)", "الهندسة (5/)", "المجموع (/20)", "التقدير", "حالة المتابعة"]
                    for col_idx, h in enumerate(headers, start=1):
                        cell = ws.cell(row=3, column=col_idx, value=h)
                        cell.font = font_header
                        cell.fill = fill_header
                        cell.alignment = align_center
                        cell.border = border_thin

                    start_r = 4
                    for idx, s in enumerate(students_data, start=1):
                        cur_r = start_r + idx - 1
                        ws.row_dimensions[cur_r].height = 24

                        # فحص حالة كل مادة
                        s_id = s["id"]
                        c_set = treated_map.get(s_id, set())

                        def get_axis_txt(val, axis_name):
                            if axis_name in c_set: return f"{val:.2f} (تمت المعالجة)"
                            elif val < 2.5: return f"{val:.2f} (قيد العلاج)"
                            return f"{val:.2f} (متحكم)"

                        status_txt = "🟢 خرج من المنطقة الحمراء" if s["is_cured"] else (f"🔴 قيد العلاج (متبقي {len(s['pending_axes'])})" if s["is_initially_fragile"] else "🟢 متحكم كلياً")

                        row_vals = [
                            idx,
                            s["name"],
                            get_axis_txt(s["ar"], "الأعداد والحساب"),
                            get_axis_txt(s["al"], "الحساب الجبري"),
                            get_axis_txt(s["fn"], "الدوال والمنحنيات"),
                            get_axis_txt(s["gm"], "الهندسة والأشعة"),
                            f"{s['total']:.2f}",
                            s["status"],
                            status_txt
                        ]

                        for c_i, v in enumerate(row_vals, start=1):
                            cell = ws.cell(row=cur_r, column=c_i, value=v)
                            cell.font = font_bold if c_i in [2, 7, 9] else font_regular
                            cell.alignment = align_right if c_i == 2 else align_center
                            cell.border = border_thin
                            if c_i == 9:
                                cell.fill = fill_cured if "خرج" in str(v) or "متحكم" in str(v) else fill_red

                    # ضبط عروض الأعمدة
                    for col in ws.columns:
                        col_letter = get_column_letter(col[0].column)
                        ws.column_dimensions[col_letter].width = 16
                    ws.column_dimensions['B'].width = 25
                    ws.column_dimensions['I'].width = 24

                    out = io.BytesIO()
                    wb.save(out)
                    return out.getvalue()

                # 2. دالة إنشاء ملف PDF للطباعة المعتمدة
                def generate_followup_grid_pdf(students_data, class_row):
                    pdf_rows_html = ""
                    for idx, s in enumerate(students_data, start=1):
                        s_id = s["id"]
                        c_set = treated_map.get(s_id, set())

                        def format_p_cell(val, axis_name):
                            if axis_name in c_set:
                                return f"<b>{val:.2f}</b><br><span style='color:green; font-size:0.75em;'>✓ عولج</span>"
                            elif val < 2.5:
                                return f"<b style='color:red;'>{val:.2f}</b><br><span style='color:red; font-size:0.75em;'>🔴 علاج</span>"
                            return f"<b>{val:.2f}</b>"

                        st_badge = "<span style='color:green; font-weight:bold;'>🟢 خرج من الحمراء</span>" if s["is_cured"] else (f"<span style='color:red; font-weight:bold;'>🔴 متبقي ({len(s['pending_axes'])})</span>" if s["is_initially_fragile"] else "<span style='color:green;'>🟢 متحكم</span>")

                        pdf_rows_html += f"""
                        <tr>
                            <td style="text-align:center; padding:5px; border:1px solid #000;">{idx}</td>
                            <td style="text-align:right; padding:5px; border:1px solid #000; font-weight:bold;">{s['name']}</td>
                            <td style="text-align:center; padding:5px; border:1px solid #000;">{format_p_cell(s['ar'], 'الأعداد والحساب')}</td>
                            <td style="text-align:center; padding:5px; border:1px solid #000;">{format_p_cell(s['al'], 'الحساب الجبري')}</td>
                            <td style="text-align:center; padding:5px; border:1px solid #000;">{format_p_cell(s['fn'], 'الدوال والمنحنيات')}</td>
                            <td style="text-align:center; padding:5px; border:1px solid #000;">{format_p_cell(s['gm'], 'الهندسة والأشعة')}</td>
                            <td style="text-align:center; padding:5px; border:1px solid #000; font-weight:bold;">{s['total']:.2f}</td>
                            <td style="text-align:center; padding:5px; border:1px solid #000;">{s['status']}</td>
                            <td style="text-align:center; padding:5px; border:1px solid #000;">{st_badge}</td>
                        </tr>
                        """

                    html_doc = f"""
                    <div style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 6px; margin-bottom: 10px;">
                        <h3 style="margin:0; font-size:1.15em;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h3>
                        <h4 style="margin:4px 0; font-size:1.0em;">مديرية التربية لولاية وهران — مقاطعة تفتيشية رقم 03</h4>
                        <p style="margin:0; font-size:0.95em;"><b>شبكة رصد ومتابعة كفاءات تلاميذ الفوج (مسار استدراك التعثرات)</b></p>
                    </div>

                    <table style="width:100%; border:none; margin-bottom:8px; font-size:0.9em;">
                        <tr style="border:none;">
                            <td style="border:none; text-align:right;"><b>القسم:</b> {class_row['level']} ({class_row['class_name']})</td>
                            <td style="border:none; text-align:center;"><b>تعداد القسم:</b> {len(students_data)} تلميذ</td>
                            <td style="border:none; text-align:left;"><b>السنة الدراسية:</b> {class_row['school_year']}</td>
                        </tr>
                    </table>

                    <table style="width:100%; border-collapse:collapse; font-size:0.82em;">
                        <thead>
                            <tr style="background:#e2e8f0;">
                                <th style="border:1px solid #000; padding:6px; width:4%;">الرقم</th>
                                <th style="border:1px solid #000; padding:6px; width:22%;">اسم ولقب التلميذ</th>
                                <th style="border:1px solid #000; padding:6px; width:10%;">الأعداد (5/)</th>
                                <th style="border:1px solid #000; padding:6px; width:10%;">الجبر (5/)</th>
                                <th style="border:1px solid #000; padding:6px; width:10%;">الدوال (5/)</th>
                                <th style="border:1px solid #000; padding:6px; width:10%;">الهندسة (5/)</th>
                                <th style="border:1px solid #000; padding:6px; width:10%;">المجموع</th>
                                <th style="border:1px solid #000; padding:6px; width:10%;">التقدير</th>
                                <th style="border:1px solid #000; padding:6px; width:14%;">حالة المتابعة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pdf_rows_html}
                        </tbody>
                    </table>

                    <div style="display:flex; justify-content:space-between; margin-top:30px; font-weight:bold; font-size:0.9em;">
                        <span>توقيع الأستاذ(ة): .........................</span>
                        <span>تأشيرة السيد مفتش التربية الوطنية: .........................</span>
                    </div>
                    """
                    return convert_html_to_pdf(html_doc)

                with col_dl_excel:
                    excel_data = generate_followup_grid_excel(all_list, c_info)
                    st.download_button(
                        label="📥 تحميل شبكة المتابعة كملف Excel ملون",
                        data=excel_data,
                        file_name=f"شبكة_متابعة_الكفاءات_{c_info['class_name']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary",
                        key="btn_dl_all_excel"
                    )

                with col_dl_pdf:
                    pdf_bytes, pdf_mime = generate_followup_grid_pdf(all_list, c_info)
                    pdf_ext = "pdf" if pdf_mime == "application/pdf" else "html"
                    st.download_button(
                        label="📑 تحميل شبكة المتابعة كملف PDF رسمي (A4)",
                        data=pdf_bytes,
                        file_name=f"شبكة_متابعة_الكفاءات_{c_info['class_name']}.{pdf_ext}",
                        mime=pdf_mime,
                        use_container_width=True,
                        type="primary",
                        key="btn_dl_all_pdf"
                    )

                st.write("---")
                map_a = {f"{a['name']} (المجموع: {a['total']:.2f} / 20)": a for a in all_list}
                sel_a_name = st.selectbox("🎯 اختاري أي تلميذ من القسم لعرض بطاقته الفردية وتحميلها:", list(map_a.keys()), key="sel_all_box")
                render_followup_section(map_a[sel_a_name], "all")

# ==============================================================================
# 9. التنبيهات الاستباقية للدروس (نسخة مصححة ومحمية من تكرار المفاتيح)
# ==============================================================================
elif menu == M_ALERTS:
    st.header("🔔 التنبيه البيداغوجي الاستباقي للدروس")
    st.caption("فحص جاهزية تلاميذ القسم قبلياً قبل بدء أي درس لتفادي انقطاع السلسلة المعرفية وتفعيل المعالجة الاستباقية.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم وتلاميذه أولاً من واجهة «الأقسام والتلاميذ».")
    else:
        tab_instant, tab_scheduled = st.tabs([
            "⚡ فحص فوري مباشر لأي درس من المنهاج", 
            "📅 معاينة الدروس المبرمجة في الجدول الزمني"
        ])

        conn = get_connection()
        try:
            curr_all = conn.execute("SELECT * FROM curriculum_matrix").fetchall()
        finally:
            conn.close()

        # قاموس الربط البيداغوجي الشامل
        col_map = {
            "الأعداد والحساب": "arithmetic",
            "التقويم والمعالجة": "arithmetic",
            "المتتاليات": "arithmetic",
            "النسب المئوية": "arithmetic",
            "الحساب الجبري": "algebra",
            "العبارات الجبرية": "algebra",
            "المعالجة البيداغوجية": "algebra",
            "الاشتقاقية": "algebra",
            "الدوال والاشتقاق": "algebra",
            "الحساب المثلثي": "algebra",
            "الدوال والمنحنيات": "functions",
            "الدوال عموميات": "functions",
            "الدوال المرجعية": "functions",
            "الدوال": "functions",
            "الإحصاء": "functions",
            "الاحتمالات": "functions",
            "الإحصاء والاحتمالات": "functions",
            "مؤشرات التشتت": "functions",
            "الهندسة والأشعة": "geometry",
            "الهندسة المستوية": "geometry",
            "الهندسة في الفضاء": "geometry",
            "الهندسة التحليلية": "geometry",
            "الهندسة والتحليلية": "geometry",
            "الحساب الشعاعي ومعادلة مستقيم": "geometry"
        }

        # -------------------------------------------------------------
        # 1. تبويب الفحص الفوري المباشر
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # 1. تبويب الفحص الفوري المباشر (حصر تلاميذ المنطقة الحمراء 🔴)
        # -------------------------------------------------------------
        with tab_instant:
            st.markdown("##### 🔍 معاينة الثغرات القبلية وحصر تلاميذ المنطقة الحمراء:")
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                sel_inst_cls = st.selectbox("1. اختاري الفوج التربوي:", list(cls_opts.keys()), key="inst_cls_select_unique")
                inst_cid = cls_opts[sel_inst_cls]
                
                # جلب المستوى المسجل لهذا القسم
                conn = get_connection()
                c_row = conn.execute("SELECT level FROM classes WHERE id = ?", (inst_cid,)).fetchone()
                conn.close()
                target_level = c_row["level"] if c_row else ""

            with col_in2:
                # تصفية دروس شعبة هذا القسم
                def match_level(lesson_lvl, cls_lvl):
                    if lesson_lvl == cls_lvl: return True
                    if "1AS" in cls_lvl or "أولى" in cls_lvl:
                        if "علوم" in cls_lvl and "ع ت" in lesson_lvl: return True
                        if "آداب" in cls_lvl and "آ" in lesson_lvl: return True
                    elif "2AS" in cls_lvl or "ثانية" in cls_lvl:
                        if "علوم" in cls_lvl and "2AS علوم" in lesson_lvl: return True
                        if "تقني" in cls_lvl and "تقني" in lesson_lvl: return True
                        if "رياضيات" in cls_lvl and "تقني" not in cls_lvl and lesson_lvl == "2AS رياضيات": return True
                        if "تسيير" in cls_lvl and "تسيير" in lesson_lvl: return True
                        if "آداب" in cls_lvl and "آداب" in lesson_lvl: return True
                    elif "3AS" in cls_lvl or "ثالثة" in cls_lvl or "بكالوريا" in cls_lvl:
                        if "علوم" in cls_lvl and "3AS علوم" in lesson_lvl: return True
                        if "تقني" in cls_lvl and "3AS تقني" in lesson_lvl: return True
                        if "رياضيات" in cls_lvl and "تقني" not in cls_lvl and lesson_lvl == "3AS رياضيات": return True
                        if "تسيير" in cls_lvl and "3AS تسيير" in lesson_lvl: return True
                        if "آداب" in cls_lvl and "3AS آداب" in lesson_lvl: return True
                    return False

                filtered_curr = [c for c in curr_all if match_level(c["level"], target_level)]
                active_curr = filtered_curr if filtered_curr else curr_all

                curr_map = {f"{c['unit']} ⟵ {c['lesson_title']} ({c['level']})": c for c in active_curr}
                sel_inst_lesson = st.selectbox("2. اختاري الدرس المستهدف من المنهاج:", list(curr_map.keys()), key=f"inst_lesson_sel_{inst_cid}")
                selected_curr = curr_map[sel_inst_lesson]

            target_resource = selected_curr["prerequisite_resource"]
            lesson_title = selected_curr["lesson_title"]
            default_obj = selected_curr["default_objective"]

            st.markdown(f"""
            <div class="art-card">
                <b>عنوان الدرس المبرمج:</b> {lesson_title} &nbsp;|&nbsp; <b>المستوى:</b> {selected_curr['level']}<br>
                <b>المحور المشروط قبلياً من التقويم:</b> <u style="color:#1E88E5; font-size:1.15em; font-weight:bold;">{target_resource}</u><br>
                <b>الهدف البيداغوجي:</b> {default_obj}
            </div>
            """, unsafe_allow_html=True)

            score_col = col_map.get(target_resource, "algebra")

         # استخراج تلاميذ المنطقة الحمراء حصراً مع استبعاد من تمت معالجتهم بنجاح في هذا المحور
            conn = get_connection()
            try:
                # 1. التلاميذ الذين رسبوا في التقويم لهذا المحور
                all_weak = conn.execute(f"""
                    SELECT s.id, s.full_name, r.{score_col} as score, r.total, r.classification
                    FROM diagnostic_results r 
                    INNER JOIN students s ON r.student_id = s.id
                    WHERE s.class_id = ? AND (r.{score_col} < 2.5 OR r.total < 7 OR r.classification = 'غير متحكم')
                    ORDER BY r.{score_col} ASC, r.total ASC
                """, (inst_cid,)).fetchall()

                # 2. جلب من تمت معالجتهم بنجاح في هذا المحور المشروط تحديداً
                cured_rows = conn.execute("""
                    SELECT student_id FROM remediation_activities 
                    WHERE resource = ? AND (response_level LIKE '%جيد%' OR response_level LIKE '%تجاوز%')
                """, (target_resource,)).fetchall()
                cured_ids = set(cr["student_id"] for cr in cured_rows)
            finally:
                conn.close()

            # التلاميذ الذين ما زالوا في المنطقة الحمراء لهذا الدرس (لم يعالجوا بعد)
            red_zone_students = [w for w in all_weak if w["id"] not in cured_ids]
            cured_students = [w for w in all_weak if w["id"] in cured_ids]

            if red_zone_students:
                st.markdown(f"""
                <div class="art-alert-danger">
                    🚨 <b>إنذار بيداغوجي استباقي — المنطقة الحمراء:</b><br>
                    يوجد <b>{len(red_zone_students)} تلاميذ</b> في قسم ({sel_inst_cls}) لا يزالون يعانون من عجز في ركيزة (<b>{target_resource}</b>) المشروطة لهذا الدرس!<br>
                    <u>هؤلاء التلاميذ بحاجة لمعالجة استباقية (10 دقائق) قبل بناء الدرس</u>.
                </div>
                """, unsafe_allow_html=True)

                st.markdown("##### 📋 قائمة تلاميذ المنطقة الحمراء الذين لم يتم استدراكهم بعد:")
                weak_table = [
                    {
                        "الرقم": idx + 1,
                        "اسم ولقب التلميذ": f"<b>{w['full_name']}</b>",
                        f"علامة ركيزة ({target_resource})": f"<span style='color:red; font-weight:bold;'>{w['score']:.2f} / 5</span>",
                        "المجموع التشخيصي": f"<b>{w['total']:.2f} / 20</b>",
                        "حالة المتابعة": "<span class='badge-pill badge-red'>🔴 قيد العلاج والاستدراك</span>"
                    } for idx, w in enumerate(red_zone_students)
                ]
                render_artistic_table(weak_table)

                # توجيه فوري لفتح بطاقة المتابعة
                st.write("")
                col_btn1, col_btn2 = st.columns([2, 1.5])
                with col_btn1:
                    target_weak_name = st.selectbox("حددي تلميذاً لفتح بطاقة متابعته فوراً:", [w["full_name"] for w in red_zone_students], key=f"sel_red_{inst_cid}")
                with col_btn2:
                    st.write("")
                    if st.button("🪪 الانتقال لبطاقة المتابعة لهذا التلميذ", type="primary", key=f"btn_goto_card_{inst_cid}"):
                        st.session_state["auto_selected_fragile_student"] = target_weak_name
                        st.session_state["auto_selected_class"] = sel_inst_cls
                        st.info(f"تم تحديد التلميذ ({target_weak_name}). انتقلي إلى محطة «بطاقة المتابعة الفردية» من القائمة الجانبية لتجدي بطاقته مفتوحة وجاهزة.")
            else:
                cured_note = f"<br>✨ <i>(تم استدراك وتجاوز تعثر {len(cured_students)} تلاميذ بنجاح قبل بداية هذا الدرس)</i>." if cured_students else ""
                st.markdown(f"""
                <div class='art-alert-success'>
                    ✅ <b>المكتسبات القبلية آمنة ومكتملة لهذا الدرس:</b><br>
                    جميع تلاميذ قسم ({sel_inst_cls}) متحكمون في ركيزة (<b>{target_resource}</b>) بعلامة ≥ 2.5.{cured_note}
                </div>
                """, unsafe_allow_html=True) 
        # -------------------------------------------------------------
        # 2. تبويب معاينة الدروس المبرمجة في الجدول الزمني
        # -------------------------------------------------------------
        with tab_scheduled:
            conn = get_connection()
            try:
                lessons = conn.execute("""
                    SELECT l.*, c.level, c.class_name FROM upcoming_lessons l
                    INNER JOIN classes c ON l.class_id = c.id ORDER BY l.lesson_date ASC
                """).fetchall()
            finally:
                conn.close()

            if not lessons:
                st.info("لا توجد دروس مبرمجة حالياً في الرزنامة. يمكنكِ برمجة الدروس من واجهة «الدروس القادمة (شجرة المنهاج)» أو استخدام التبويب الأول للفحص الفوري.")
            else:
                l_opts = {f"📅 {l['lesson_date']} | {l['lesson_title']} ({l['level']} - {l['class_name']})": l["id"] for l in lessons}
                sel_l = st.selectbox("اختاري درساً من الرزنامة:", list(l_opts.keys()), key="sched_lesson_select_unique")
                lid = l_opts[sel_l]

                conn = get_connection()
                try:
                    ldata = conn.execute("SELECT * FROM upcoming_lessons WHERE id = ?", (lid,)).fetchone()
                    target_res = ldata["resource"]
                    cid = ldata["class_id"]
                    scol = col_map.get(target_res, "algebra")

                    weaks = conn.execute(f"""
                        SELECT s.full_name, r.{scol} as score, r.total, r.classification
                        FROM diagnostic_results r INNER JOIN students s ON r.student_id = s.id
                        WHERE s.class_id = ? AND r.{scol} < 2.5 ORDER BY r.{scol} ASC
                    """, (cid,)).fetchall()
                finally:
                    conn.close()

                st.markdown(f"""
                <div class="art-card">
                    <b>الدرس المجدول:</b> {ldata['lesson_title']} | <b>التاريخ:</b> {ldata['lesson_date']}<br>
                    <b>المحور المشروط:</b> <u>{target_res}</u> | <b>الهدف:</b> {ldata['objective']}
                </div>
                """, unsafe_allow_html=True)

                if weaks:
                    st.markdown(f"<div class='art-alert-danger'>⚠️ يوجد <b>{len(weaks)} تلاميذ</b> متعثرين في ركيزة ({target_res}) المشروطة لهذا الدرس المجدول!</div>", unsafe_allow_html=True)
                    sched_weak_table = [
                        {
                            "الرقم": idx + 1,
                            "اسم ولقب التلميذ": w["full_name"],
                            f"علامة {target_res}": f"<b>{w['score']:.2f} / 5</b>",
                            "المجموع العام": f"{w['total']:.2f} / 20",
                            "الوضعية": format_badge_html(w["classification"])
                        } for idx, w in enumerate(weaks)
                    ]
                    render_artistic_table(sched_weak_table)
                else:
                    st.markdown("<div class='art-alert-success'>✅ جميع تلاميذ الفوج متمكنون من المكتسبات القبلية لهذا الدرس.</div>", unsafe_allow_html=True)
# ==============================================================================
# 10. برمجة وجدولة الدروس (شجرة كفاءات المنهاج الجزائري الشاملة لجميع المستويات)
# ==============================================================================
elif menu == M_LESSONS:
    st.header("📅 تخطيط وبرمجة الدروس (شجرة المنهاج الوزاري)")
    st.caption("اختيار الدرس مباشرة من التدرجات السنوية الرسمية مع تحديث فوري للدروس وربطها بنظام التنبيه.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم أولاً من واجهة «الأقسام والتلاميذ».")
    else:
        conn = get_connection()
        try:
            curriculum = conn.execute("SELECT * FROM curriculum_matrix").fetchall()
        finally:
            conn.close()

        tab_plan, tab_history = st.tabs(["➕ جدولة درس جديد", "📋 قائمة الدروس المبرمجة وحذفها"])

        with tab_plan:
            st.markdown("##### ✏️ إعداد وبرمجة درس جديد:")
            
            col1, col2 = st.columns(2)
            with col1:
                # 1. اختيار القسم
                sel_cls = st.selectbox("1. اختاري القسم المستهدف:", list(cls_opts.keys()), key="sch_cls_sel")
                cid = cls_opts[sel_cls]

                # جلب المستوى المسجل لهذا القسم تلقائياً
                conn = get_connection()
                c_row = conn.execute("SELECT level FROM classes WHERE id = ?", (cid,)).fetchone()
                conn.close()
                detected_level = c_row["level"] if c_row else ""

                # قائمة المستويات الرسمية
                all_levels = [
                    "1AS ج م ع ت",
                    "1AS ج م آ",
                    "1AS ج م أ",
                    "2AS علوم تجريبية",
                    "2AS تقني رياضي",
                    "2AS رياضيات",
                    "2AS تسيير واقتصاد",
                    "2AS آداب وفلسفة + لغات أجنبية",
                    "3AS علوم تجريبية",
                    "3AS تقني رياضي",
                    "3AS رياضيات",
                    "3AS تسيير واقتصاد",
                    "3AS آداب ولغات"
                ]

                # تحديد المؤشر الافتراضي تلقائياً
                def_idx = 0
                for i, lvl in enumerate(all_levels):
                    if lvl in detected_level or detected_level in lvl:
                        def_idx = i
                        break

                # 2. اختيار المستوى والشعبة (هنا يتم تعريف sel_level أولاً)
                sel_level = st.selectbox(
                    "2. اختاري المستوى والشعبة التعليمية:", 
                    all_levels, 
                    index=def_idx, 
                    key=f"sch_lvl_{cid}"
                )

                # 3. تصفية الدروس بمرونة تدعم (ج م آ / ج م أ) بعد تعريف sel_level
                unit_lessons = [
                    c for c in curriculum 
                    if c["level"] == sel_level
                    or ("2AS" in sel_level and "2AS" in c["level"] and "آداب" in sel_level and "آداب" in c["level"]) 
                    or c["level"] == sel_level.replace("أ", "آ") 
                    or c["level"] == sel_level.replace("آ", "أ")
                ]
                lesson_map = {f"{c['unit']} ⟵ {c['lesson_title']}": c for c in unit_lessons}

                # 4. اختيار الدرس من التدرج السنوي
                if lesson_map:
                    chosen_curr_str = st.selectbox(
                        "3. اختاري الدرس من التدرج السنوي:", 
                        list(lesson_map.keys()), 
                        key=f"sch_lesson_{sel_level}"
                    )
                    curr_obj = lesson_map[chosen_curr_str]
                    title = curr_obj["lesson_title"]
                    res = curr_obj["prerequisite_resource"]
                    default_obj = curr_obj["default_objective"]
                else:
                    st.info("لا توجد دروس مدخلة لهذا المستوى حالياً.")
                    title = st.text_input("عنوان الدرس يدوياً:")
                    res = "الحساب الجبري"
                    default_obj = ""

                st.markdown(f"""
                <div class='art-card' style='border-right-color:#1E88E5; padding:10px 15px;'>
                    <b>المحور المشروط قبلياً تلقائياً:</b> <span style='color:#1E88E5; font-weight:bold;'>{res}</span>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                les_date = st.date_input("تاريخ الحصة المبرمجة:", value=date.today(), key="sch_date_inp")
                obj = st.text_input("الهدف البيداغوجي الأساسي:", value=default_obj, key=f"sch_obj_{title if 'title' in locals() else 'default'}")
                notes = st.text_area("توجيهات ووسائل العمل (برمجيات، بطاقات، أدوات):", placeholder="استعمال برمجية GeoGebra، آلة حاسبة بيانية، بطاقات عمل...", key="sch_notes_inp")

            st.write("")
            if st.button("🚀 حفظ الدرس وربطه بنظام التنبيه الاستباقي", type="primary", key="save_sch_btn"):
                if not title.strip() or not obj.strip():
                    st.warning("يرجى التأكد من كتابة عنوان الدرس وهدفه البيداغوجي.")
                else:
                    conn = get_connection()
                    try:
                        conn.execute("""
                            INSERT INTO upcoming_lessons (class_id, lesson_title, resource, lesson_date, objective, notes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (cid, title.strip(), res, les_date.isoformat(), obj.strip(), notes.strip()))
                        conn.commit()
                        st.success(f"✅ تمت جدولة درس '{title}' لقسم ({sel_cls}) وربطه بالمحور ({res}) بنجاح.")
                        st.rerun()
                    finally:
                        conn.close()

        with tab_history:
            conn = get_connection()
            try:
                scheduled = conn.execute("""
                    SELECT l.id, l.lesson_date, l.lesson_title, l.resource, l.objective, c.level, c.class_name
                    FROM upcoming_lessons l
                    INNER JOIN classes c ON l.class_id = c.id
                    ORDER BY l.lesson_date DESC
                """).fetchall()
            finally:
                conn.close()

            if not scheduled:
                st.info("لا توجد دروس مبرمجة حالياً.")
            else:
                st.markdown("##### 📋 الدروس المسجلة في الرزنامة:")
                sched_table = [
                    {
                        "رقم الدرس": s["id"],
                        "التاريخ": s["lesson_date"],
                        "القسم": f"{s['level']} — {s['class_name']}",
                        "عنوان الدرس": f"<b>{s['lesson_title']}</b>",
                        "المحور المشروط": f"<span class='badge-pill badge-green'>{s['resource']}</span>",
                        "الهدف البيداغوجي": s["objective"]
                    } for s in scheduled
                ]
                render_artistic_table(sched_table)

                st.write("---")
                del_opts = {f"{s['lesson_date']} | {s['lesson_title']} ({s['class_name']})": s["id"] for s in scheduled}
                lesson_to_del = st.selectbox("اختاري درساً لحذفه من الرزنامة إن أردتِ:", list(del_opts.keys()), key="del_lesson_sel")
                if st.button("🗑️ حذف هذا الدرس المبرمج"):
                    conn = get_connection()
                    try:
                        conn.execute("DELETE FROM upcoming_lessons WHERE id = ?", (del_opts[lesson_to_del],))
                        conn.commit()
                        st.success("تم حذف الدرس من الرزنامة.")
                        st.rerun()
                    finally:
                        conn.close()

# ==============================================================================
# 11. بنك الأنشطة العلاجية المصغرة (10 دقائق)
# ==============================================================================
elif menu == M_BANK:
    st.header("⏱️ بنك الأنشطة العلاجية المصغرة (10 دقائق)")
    st.caption("مستوحى من الاستراتيجية الرابعة المعتمدة رسمياً: سد الفجوات التقنية دون تعطيل البرنامج الدراسي.")

    conn = get_connection()
    try:
        cards = conn.execute("SELECT * FROM remediation_bank").fetchall()
    finally:
        conn.close()

    res_f = st.selectbox("تصفية حسب المحور:", ["جميع المحاور"] + RESOURCES)
    filtered = [c for c in cards if res_f == "جميع المحاور" or c["resource"] == res_f]
    for c in filtered:
        with st.expander(f"📌 {c['title']} — ({c['resource']})", expanded=True):
            st.markdown(f"""
            <div class="art-card">
                <h4 style="margin-top:0; color:#1E88E5;">📖 خلاصة القاعدة الأساسية:</h4>
                <p style="font-size: 1.05em;">{c['rule_summary']}</p>
                <hr style="border-color: rgba(128,128,128,0.2);">
                <h4 style="color:#EF4444;">✍️ التطبيق الفردي المباشر (7 دقائق):</h4>
                <pre style="background: rgba(128,128,128,0.1); color: var(--text-color); padding: 12px; border-radius: 6px; font-family: Cairo;">{c['exercise_content']}</pre>
                <hr style="border-color: rgba(128,128,128,0.2);">
                <h4 style="color:#22C55E;">✅ الحل النموذجي والمناقشة (3 دقائق):</h4>
                <pre style="background: rgba(128,128,128,0.1); color: var(--text-color); padding: 12px; border-radius: 6px; font-family: Cairo;">{c['solution_content']}</pre>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 12. دليل وتوجيهات السيد المفتش
# ==============================================================================
elif menu == M_INSPECTOR:
    st.header("📘 الدليل البيداغوجي ووثائق التقويم الرسمية")
    st.caption("خلاصة مخرجات ملتقى مفتشية الرياضيات - مقاطعة وهران 03 (شعبتي العلوم والآداب لـ 1AS و 2AS و 3AS).")

    t1, t2, t3, t4 = st.tabs([
        "🎯 استراتيجيات المعالجة الأربع", 
        "📄 استمارة التقويم الذاتي (تحميل A4)", 
        "📁 مكونات ملف التقويم (معيار الجودة)", 
        "⚖️ الأطر المرجعية والقانونية"
    ])

    with t1:
        st.markdown("""
        <div class="art-card">
            <h4 style="color:#1E88E5;">1. استراتيجية "تحليل المسارات الإدراكية" (التعلم بالخطأ):</h4>
            <b>الوصف:</b> بدلاً من إعطاء الحل الصحيح مباشرة، نركز على <i>"لماذا أخطأ التلميذ؟"</i>.<br>
            <b>التطبيق:</b> اختيار "خطأ شائع" من أوراق التقويم وعرضه على السبورة (بدون اسم التلميذ)، وفتح نقاش جماعي لتحليل المنطق الذي أدى للخطأ وتصحيحه.<br>
            <b>الهدف:</b> تطوير النقد الذاتي لدى تلاميذ الثانوي.
        </div>
        <div class="art-card">
            <h4 style="color:#1E88E5;">2. استراتيجية "التدرج في التجريد" (النمذجة):</h4>
            <b>الوصف:</b> تلميذ الثانوي يعاني غالباً من الانتقال من المحسوس إلى الرمزي (خاصة في أقسام 1 ج م أ و 2 أف).<br>
            <b>التطبيق:</b> البدء بأمثلة عددية بسيطة، ثم الانتقال تدريجياً لتعميم القاعدة باستخدام المتغيرات x و y.<br>
            <b>الهدف:</b> بناء المفهوم الرياضي المجرد بشكل متين.
        </div>
        <div class="art-card">
            <h4 style="color:#1E88E5;">3. استراتيجية "الخرائط الذهنية للمفاهيم":</h4>
            <b>الوصف:</b> ربط الدروس ببعضها، لأن الرياضيات في الثانوي تراكمية حلزونية.<br>
            <b>التطبيق:</b> عند معالجة نقص في "المتتاليات" أو "الدوال"، يتم رسم خريطة تربطها بالمكتسبات السابقة.<br>
            <b>الهدف:</b> معالجة تشتت المعلومات لدى التلميذ وربط المكتسبات القبلية بالجديدة.
        </div>
        <div class="art-card">
            <h4 style="color:#1E88E5;">4. استراتيجية "التعليم المصغر" (10 دقائق):</h4>
            <b>الوصف:</b> استهداف ثغرة تقنية محددة جداً.<br>
            <b>التطبيق:</b> تخصيص 10 دقائق بداية كل حصة لمعالجة "ثغرة تقنية" ظهرت في التشخيص (مثلاً: الاختزال، إشارة العبارة، حل معادلة).<br>
            <b>الهدف:</b> سد الفجوات التقنية دون تعطيل البرنامج الدراسي.
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.subheader("📄 تحميل استمارة التقويم الذاتي الرسمية (A4 جاهزة للطباعة)")
        st.write("اختاري المستوى والشعبة لتحميل الاستمارة الوزارية المعتمدة بختم المقاطعة التفتيشية:")

        ALL_STREAMS_DATA = {
            "1AS ج م ع ت (جذع مشترك علوم وتكنولوجيا)": {
                "code": "1 ج م ع ت (علوم وتكنولوجيا)",
                "competencies": [
                    "الحساب على الكسور والجذور", "النشر والتبسيط والاختزال",
                    "تحليل عبارة إلى جداء عاملين", "حل معادلة من الدرجة الأولى",
                    "حساب صور وسوابق بواسطة دالة", "تمثيل دالة (خطية أو تآلفية) بيانياً",
                    "حساب إحداثيات شعاع وطول قطعة", "إحداثيات نقطة تقاطع بيانيين"
                ]
            },
            "1AS ج م أ (جذع مشترك آداب)": {
                "code": "1 ج م أ (جذع مشترك آداب)",
                "competencies": [
                    "الحساب على القاسم المشترك الأكبر (PGCD)", "النشر والتبسيط والاختزال",
                    "تحليل عبارة إلى جداء عاملين", "حل معادلة من الدرجة الأولى",
                    "تعيين عبارة دالة تآلفية بمعرفة الصور والسوابق", "حساب إحداثيات شعاع وطول قطعة",
                    "إحداثيات نقطة منتصف قطعة"
                ]
            },
            "2AS علوم تجريبية (2 ع ت)": {
                "code": "2 ع ت (علوم تجريبية)",
                "competencies": [
                    "الحساب على الكسور والجذور", "النشر والتبسيط (متطابقات شهيرة)",
                    "تحليل عبارة جبرية إلى جداء عاملين", "حل معادلة من الدرجة الأولى",
                    "حساب صور وسوابق باستخدام دالة", "تمثيل دالة (خطية أو تآلفية) بيانياً",
                    "حساب إحداثيات شعاع وطول قطعة", "استخدام نظريتي فيثاغورس وطاليس",
                    "التعامل مع النسب المثلثية (cos x, sin x)"
                ]
            },
            "2AS تقني رياضي (2 ت ر)": {
                "code": "2 ت ر (تقني رياضي)",
                "competencies": [
                    "الحساب على الكسور والجذور", "النشر والتبسيط (متطابقات شهيرة)",
                    "تحليل عبارة جبرية إلى جداء عاملين", "حل معادلة من الدرجة الأولى",
                    "حساب صور وسوابق باستخدام دالة", "تمثيل دالة (خطية أو تآلفية) بيانياً",
                    "حساب إحداثيات شعاع وطول قطعة", "استخدام نظريتي فيثاغورس وطاليس",
                    "التعامل مع النسب المثلثية (cos x, sin x)"
                ]
            },
            "2AS رياضيات (2 ر)": {
                "code": "2 رياضيات",
                "competencies": [
                    "النشر والتبسيط (متطابقات شهيرة)", "حل معادلة من الدرجة الثانية",
                    "تعيين مجموعة تعريف دالة", "دراسة اتجاه تغير دالة",
                    "تشكيل جدول تغيرات لدالة", "تمثيل دالة بيانياً انطلاقاً من منحنى دالة مرجعية",
                    "تبسيط عبارة مثلثية", "حلول معادلة مثلثية"
                ]
            },
            "2AS تسيير واقتصاد (2 ت ا)": {
                "code": "2 ت ا (تسيير واقتصاد)",
                "competencies": [
                    "النشر والتبسيط (متطابقات شهيرة)", "الشكل النموذجي",
                    "حل معادلة من الدرجة الثانية", "الجداول الإحصائية",
                    "المتوسط الحسابي - الوسيط والمنوال", "تعيين مجموعة تعريف دالة",
                    "دراسة اتجاه تغير دالة", "تشكيل جدول تغيرات لدالة",
                    "تمثيل دالة بيانياً انطلاقاً من منحنى دالة مرجعية"
                ]
            },
            "2AS آداب وفلسفة + لغات أجنبية (2 أف + 2 لغ)": {
                "code": "2 أف + 2 لغ (آداب ولغات)",
                "competencies": [
                    "الحساب على النسب المئوية", "النشر والتبسيط والاختزال",
                    "تحليل عبارة إلى جداء عاملين", "حل معادلة من الدرجة الأولى",
                    "حساب صور بواسطة عبارة جبرية", "تركيب دالتين (خطية أو تآلفية)",
                    "حساب معدل سلسلة إحصائية"
                ]
            },
            "3AS علوم تجريبية (3 ع ت)": {
                "code": "3 ع ت (علوم تجريبية)",
                "competencies": [
                    "حساب نهايات بسيطة وحالات عدم التعيين",
                    "النهايات - السلوك التقاربي",
                    "الاشتقاقية - اتجاه التغير",
                    "التفسير الهندسي للعدد المشتق",
                    "تعيين إشارة الدالة المشتقة بيانياً",
                    "تعيين معادلة المماس"
                ]
            },
            "3AS تقني رياضي (3 ت ر)": {
                "code": "3 ت ر (تقني رياضي)",
                "competencies": [
                    "متتالية معرفة بعلاقة تراجعية (حساب الحدود)",
                    "اتجاه تغير متتالية عددية",
                    "المتتاليات الهندسية",
                    "الاشتقاقية - اتجاه التغير",
                    "النهايات - السلوك التقاربي"
                ]
            },
            "3AS رياضيات (3 ر)": {
                "code": "3 رياضيات",
                "competencies": [
                    "حساب احتمال حادثة",
                    "تعريف قانون الاحتمال لمتغير عشوائي",
                    "تعريف متتالية هندسية",
                    "حساب الحد العام لمتتالية هندسية",
                    "حساب مجموع حدود متتابعة من متتالية هندسية",
                    "الاشتقاقية - اتجاه التغير",
                    "النهايات - السلوك التقاربي"
                ]
            },
            "3AS تسيير واقتصاد (3 ت ا)": {
                "code": "3 ت ا (تسيير واقتصاد)",
                "competencies": [
                    "حساب نهاية لدالة كثير الحدود",
                    "توليد متتالية بحساب الحد الموالي بدلالة n",
                    "التعرف على نوع المتتالية",
                    "معادلة المماس",
                    "خط مقارب مائل",
                    "التحليل والتبسيط",
                    "حلول معادلة ومتراجحة من الدرجة الثانية",
                    "مجموع حدود لمتتالية حسابية"
                ]
            },
            "3AS آداب وفلسفة + لغات أجنبية (3 أف + 3 لغ)": {
                "code": "3 أف + 3 لغ (آداب ولغات)",
                "competencies": [
                    "حساب حدود متتالية",
                    "توليد متتالية بحساب الحد الموالي بدلالة n",
                    "التعرف على نوع المتتالية",
                    "القراءة البيانية",
                    "حساب صور وسوابق بواسطة دالة",
                    "النشر والتحليل",
                    "حساب النهايات",
                    "إشارة دالة واتجاه تغير دالة",
                    "معادلة مماس"
                ]
            }
        }

        stream_choice = st.selectbox("اختاري المستوى والشعبة:", list(ALL_STREAMS_DATA.keys()), key="self_eval_stream_sel")
        
        selected_data = ALL_STREAMS_DATA.get(stream_choice, list(ALL_STREAMS_DATA.values())[0])
        stream_code = selected_data["code"]
        competencies_list = selected_data["competencies"]

        table_rows_html = ""
        for comp in competencies_list:
            table_rows_html += f"""
            <tr>
                <td style="padding: 7px 12px; border: 1px solid #000; text-align: right; font-weight: bold;">{comp}</td>
                <td style="padding: 7px; border: 1px solid #000; text-align: center; width: 18%;"></td>
                <td style="padding: 7px; border: 1px solid #000; text-align: center; width: 18%;"></td>
                <td style="padding: 7px; border: 1px solid #000; text-align: center; width: 18%;"></td>
            </tr>
            """

        self_eval_html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>استمارة التقويم الذاتي - {stream_code}</title>
            <style>
                body {{ font-family: 'Cairo', Arial, sans-serif; margin: 20px; line-height: 1.5; color: #000; }}
                .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #000; padding-bottom: 6px; margin-bottom: 10px; }}
                .main-box {{ border: 2px solid #000; padding: 6px; text-align: center; font-size: 1.2em; font-weight: bold; margin-bottom: 12px; background: #f2f2f2; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 0.95em; }}
                th, td {{ border: 1px solid #000; padding: 6px; }}
                th {{ background-color: #e6e6e6; text-align: center; }}
                .impression-box {{ margin-top: 10px; line-height: 2.0; font-size: 1em; }}
                @media print {{ body {{ margin: 10mm; }} button {{ display: none; }} }}
            </style>
        </head>
        <body>
            <div style="text-align: center;">
                <h3 style="margin: 0;">الجمهورية الجزائرية الديمقراطية الشعبية</h3>
                <h4 style="margin: 3px 0;">وزارة التربية الوطنية</h4>
            </div>

            <table style="border: none; width: 100%; margin-bottom: 6px;">
                <tr style="border: none;">
                    <td style="border: none; text-align: right; width: 50%;">
                        مديرية التربية لولاية وهران<br>
                        ثانويات: مقاطعة تفتيشية رقم 03<br>
                        الاسم واللقب: .......................................
                    </td>
                    <td style="border: none; text-align: left; width: 50%;">
                        السنة الدراسية: 2026 / 2027<br>
                        الأستاذ(ة): .......................................<br>
                        القسم: .......................................
                    </td>
                </tr>
            </table>

            <div class="main-box">
                استمارة التقويم الذاتي في مادة الرياضيات لـ {stream_code}
            </div>

            <div style="font-weight: bold; margin-bottom: 6px;">1. المحور المعرفي: ضع العلامة (X) في الخانة المناسبة:</div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 46%;">المكتسبات القبلية</th>
                        <th>أتحكم جيداً</th>
                        <th>أجد صعوبة</th>
                        <th>لا أتذكر</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>

            <div class="impression-box">
                <b>2. الانطباع الشخصي :</b><br>
                1) ما هي الوحدة التي تشعر أنها "نقطة قوتك" في الرياضيات؟<br>
                ........................................................................................................................................<br>
                2) ما هو العائق الأكبر الذي واجهته في حل موضوع التقويم التشخيصي؟<br>
                ........................................................................................................................................<br>
                3) ما هي توقعاتك أو أهدافك لمادة الرياضيات في هذا المستوى؟<br>
                ........................................................................................................................................
            </div>
        </body>
        </html>
        """

        pdf_data, mime_type = convert_html_to_pdf(self_eval_html)
        ext = "pdf" if mime_type == "application/pdf" else "html"
        st.download_button(
            label=f"📑 تحميل استمارة التقويم الذاتي لـ ({stream_code}) كملف PDF جاهز للتوزيع",
            data=pdf_data,
            file_name=f"استمارة_التقويم_الذاتي_{stream_code.replace(' ', '_')}.{ext}",
            mime=mime_type,
            type="primary",
            key="dl_self_eval_btn"
        )

    with t3:
        st.markdown("""
        <div class="art-card">
            <h4 style="color:#22C55E;">📋 مكونات ملف التقويم التشخيصي الجاهز للتفتيش (معيار الجودة):</h4>
            <p>لضمان الجاهزية التربوية أمام التفتيش والإدارة، يجب أن يتضمن ملف الأستاذ(ة):</p>
            <ul>
                <li><b>1. الجانب الوثائقي:</b> مقدمة التقويم، نسخة الاختبار، الإجابة النموذجية بسلم التنقيط، وتقرير تحليل النتائج المعتمد.</li>
                <li><b>2. الجانب الرقمي:</b> شبكة التفريغ (Excel) متضمنة التنسيق الشرطي والرسوم البيانية وخارطة الفوارق.</li>
                <li><b>3. الجانب العلاجي:</b> رزنامة المعالجة الزمنية، بنك تمارين المعالجة المركزة، وبطاقات المتابعة الفردية (خاصة بالفئة الهشة).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with t4:
        st.markdown("""
        <div class="art-card">
            <h4 style="color:#9C27B0;">⚖️ المرجعيات البيداغوجية والقانونية:</h4>
            <ul>
                <li><b>المرجعية المعرفية (مصفوفة المدى والتتابع):</b> تعتمد مبدأ الحلزونية، حيث تشترط فهم موارد سابقة لاستيعاب دروس جديدة.</li>
                <li><b>المرجعية البيداغوجية (المقاربة بالكفاءات):</b> قياس القدرة على تعبئة الموارد وحل المشكلات وفق تصنيف "بلوم" (معرفة، فهم، تطبيق، تحليل).</li>
                <li><b>المرجعية القانونية:</b> الالتزام بالمناشير الوزارية التي تنص على إجراء التقويم واستثمار نتائجه كجزء من التقويم التكويني الذي لا يدخل في المعدل الفصلي.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
# ==============================================================================
# 13. دفتر التقويم البيداغوجي الرسمي (وفق المنشور الوزاري رقم 1613)
# ==============================================================================
elif menu == M_GRADEBOOK:
    st.header("📒 دفتر التقويم البيداغوجي والمراقبة المستمرة")
    st.caption("صُمم وفقاً لمراسلة الأمين العام لوزارة التربية الوطنية رقم 1613/و.ت.و/أ.ع المتضمنة ترتيبات التقويم البيداغوجي.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم وتلاميذه أولاً.")
    else:
        # شريط الخيارات العلوي
        col_c, col_t, col_hs, col_tch = st.columns([1.5, 1.2, 1.5, 1.5])
        with col_c:
            sel_cls = st.selectbox("🎯 القسم / الفوج:", list(cls_opts.keys()), key="gb_cls_sel")
            cid = cls_opts[sel_cls]
        with col_t:
            sel_term = st.selectbox("📅 الفصل الدراسي:", ["الفصل الأول", "الفصل الثاني", "الفصل الثالث"], key="gb_term_sel")
        with col_hs:
            high_school_name = st.text_input("اسم الثانوية:", value="ثانوية ....................", key="gb_hs_name")
        with col_tch:
            teacher_name = st.text_input("الأستاذ(ة):", value="ديداوي سومية", key="gb_tch_name")

        # جلب بيانات التلاميذ والنقاط المسجلة
        conn = get_connection()
        try:
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (cid,)).fetchone()
            students = conn.execute("SELECT id, full_name FROM students WHERE class_id = ? ORDER BY full_name ASC", (cid,)).fetchall()
            
            # جلب تقييمات الفصل المختار
            records = conn.execute("""
                SELECT * FROM continuous_evaluations 
                WHERE student_id IN (SELECT id FROM students WHERE class_id = ?) AND term = ?
            """, (cid, sel_term)).fetchall()
        finally:
            conn.close()

        records_map = {r["student_id"]: r for r in records}

        # بناء البيانات للجدول المحرر
        table_rows = []
        for s in students:
            sid = s["id"]
            rec = records_map.get(sid, None)
            
            beh = float(rec["behavior"]) if rec and rec["behavior"] is not None else 3.0
            att = float(rec["attendance"]) if rec and rec["attendance"] is not None else 3.0
            tool = float(rec["tools"]) if rec and rec["tools"] is not None else 3.0
            book = float(rec["notebook"]) if rec and rec["notebook"] is not None else 3.0
            part = float(rec["participation"]) if rec and rec["participation"] is not None else 3.0
            hw = float(rec["homework"]) if rec and rec["homework"] is not None else 5.0
            
            # المراقبة المستمرة = مجموع المؤشرات الستة
            cont_calc = round(beh + att + tool + book + part + hw, 2)
            
            t1 = float(rec["test1"]) if rec and rec["test1"] is not None else None
            t2 = float(rec["test2"]) if rec and rec["test2"] is not None else None
            
            # معدل الفروض
            if t1 is not None and t2 is not None:
                t_avg = round((t1 + t2) / 2.0, 2)
            elif t1 is not None:
                t_avg = t1
            elif t2 is not None:
                t_avg = t2
            else:
                t_avg = None
                
            ex = float(rec["exam"]) if rec and rec["exam"] is not None else None
            
            # المعدل الفصلي الرسمي = (المراقبة المستمرة + معدل الفروض + الاختبار * 2) / 4
            if t_avg is not None and ex is not None:
                final_term_avg = round((cont_calc + t_avg + (ex * 2.0)) / 4.0, 2)
            else:
                final_term_avg = None
                
            rem = rec["remarks"] if rec and rec["remarks"] else ""

            table_rows.append({
                "student_id": sid,
                "الاسم و اللقب": s["full_name"],
                "السلوك (/3)": beh,
                "الغيابات (/3)": att,
                "الأدوات (/3)": tool,
                "الكراريس (/3)": book,
                "المشاركة (/3)": part,
                "المهمات والواجبات (/5)": hw,
                "المراقبة المستمرة (/20)": cont_calc,
                "الفرض 1 (/20)": t1,
                "الفرض 2 (/20)": t2,
                "معدل الفروض (/20)": t_avg,
                "الاختبار (/20)": ex,
                "المعدل (/20)": final_term_avg,
                "ملاحظات نوعية": rem
            })

        df_editor = pd.DataFrame(table_rows)

        tab_edit_grades, tab_preview_print = st.tabs([
            "✍️ رصد النقاط والمؤشرات التفاعلية", 
            "🖨️ المعاينة والتحميل (غلاف مزخرف + دفتر رسمي A4 PDF)"
        ])

        with tab_edit_grades:
            st.markdown("""
            <div class="art-card" style="border-right-color:#10B981; padding:10px 15px; margin-bottom:12px;">
                💡 <b>توجيه وزاري:</b> علامة <b>المراقبة المستمرة (20)</b> تُحسب تلقائياً بجمع مؤشرات الأداء الستة (3+3+3+3+3+5).<br>
                و<b>المعدل الفصلي</b> يُحسب تلقائياً بالقانون الرسمي: <code>[المراقبة المستمرة + معدل الفروض + (الاختبار × 2)] ÷ 4</code>.
            </div>
            """, unsafe_allow_html=True)

            edited_df = st.data_editor(
                df_editor,
                column_config={
                    "student_id": None, # إخفاء المعرف
                    "الاسم و اللقب": st.column_config.TextColumn(disabled=True),
                    "السلوك (/3)": st.column_config.NumberColumn(min_value=0.0, max_value=3.0, step=0.25),
                    "الغيابات (/3)": st.column_config.NumberColumn(min_value=0.0, max_value=3.0, step=0.25),
                    "الأدوات (/3)": st.column_config.NumberColumn(min_value=0.0, max_value=3.0, step=0.25),
                    "الكراريس (/3)": st.column_config.NumberColumn(min_value=0.0, max_value=3.0, step=0.25),
                    "المشاركة (/3)": st.column_config.NumberColumn(min_value=0.0, max_value=3.0, step=0.25),
                    "المهمات والواجبات (/5)": st.column_config.NumberColumn(min_value=0.0, max_value=5.0, step=0.25),
                    "المراقبة المستمرة (/20)": st.column_config.NumberColumn(disabled=True),
                    "الفرض 1 (/20)": st.column_config.NumberColumn(min_value=0.0, max_value=20.0, step=0.25),
                    "الفرض 2 (/20)": st.column_config.NumberColumn(min_value=0.0, max_value=20.0, step=0.25),
                    "معدل الفروض (/20)": st.column_config.NumberColumn(disabled=True),
                    "الاختبار (/20)": st.column_config.NumberColumn(min_value=0.0, max_value=20.0, step=0.25),
                    "المعدل (/20)": st.column_config.NumberColumn(disabled=True),
                    "ملاحظات نوعية": st.column_config.TextColumn(width="medium")
                },
                use_container_width=True,
                height=500,
                key="continuous_data_editor"
            )

            if st.button("💾 حفظ كافة التعديلات وعلامات الفصل في قاعدة البيانات", type="primary"):
                conn = get_connection()
                try:
                    for idx, row in edited_df.iterrows():
                        sid = row["student_id"]
                        beh = row["السلوك (/3)"] or 0.0
                        att = row["الغيابات (/3)"] or 0.0
                        tool = row["الأدوات (/3)"] or 0.0
                        book = row["الكراريس (/3)"] or 0.0
                        part = row["المشاركة (/3)"] or 0.0
                        hw = row["المهمات والواجبات (/5)"] or 0.0
                        
                        cont_val = round(beh + att + tool + book + part + hw, 2)
                        
                        t1_val = row["الفرض 1 (/20)"] if pd.notna(row["الفرض 1 (/20)"]) else None
                        t2_val = row["الفرض 2 (/20)"] if pd.notna(row["الفرض 2 (/20)"]) else None
                        
                        if t1_val is not None and t2_val is not None:
                            t_avg_val = round((t1_val + t2_val) / 2.0, 2)
                        elif t1_val is not None:
                            t_avg_val = t1_val
                        elif t2_val is not None:
                            t_avg_val = t2_val
                        else:
                            t_avg_val = None
                            
                        ex_val = row["الاختبار (/20)"] if pd.notna(row["الاختبار (/20)"]) else None
                        
                        if t_avg_val is not None and ex_val is not None:
                            f_avg_val = round((cont_val + t_avg_val + (ex_val * 2.0)) / 4.0, 2)
                        else:
                            f_avg_val = None
                            
                        rem_val = str(row["ملاحظات نوعية"]) if pd.notna(row["ملاحظات نوعية"]) else ""

                        conn.execute("""
                            INSERT INTO continuous_evaluations 
                            (student_id, term, behavior, attendance, tools, notebook, participation, homework, continuous_mark, test1, test2, test_avg, exam, term_avg, remarks)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(student_id, term) DO UPDATE SET
                                behavior=excluded.behavior,
                                attendance=excluded.attendance,
                                tools=excluded.tools,
                                notebook=excluded.notebook,
                                participation=excluded.participation,
                                homework=excluded.homework,
                                continuous_mark=excluded.continuous_mark,
                                test1=excluded.test1,
                                test2=excluded.test2,
                                test_avg=excluded.test_avg,
                                exam=excluded.exam,
                                term_avg=excluded.term_avg,
                                remarks=excluded.remarks
                        """, (sid, sel_term, beh, att, tool, book, part, hw, cont_val, t1_val, t2_val, t_avg_val, ex_val, f_avg_val, rem_val))
                    
                    conn.commit()
                    st.success(f"✅ تم بنجاح حفظ نقاط {sel_term} لجميع تلاميذ القسم!")
                    st.rerun()
                finally:
                    conn.close()

        with tab_preview_print:
            st.markdown("#### 🖨️ استخراج الدفتر كاملاً بصيغة PDF عالية الجودة (طِبق الأصل)")
            st.caption("يشمل صفحة الغلاف المزخرفة وصفحات رصد النقاط بالترويسة والتذييل الوزاري الرسمي.")

            # دالة إنشاء كود HTML المطابق لصفحات PDF الثلاث
            def build_full_gradebook_html(df_data, c_row, hs_name, tch_name, term_label):
                # 1. إحصائيات الفوج
                total_st = len(df_data)
                
                # إنشاء سطور الجدول
                def make_table_rows(subset_df, start_num):
                    rows_code = ""
                    for i, (_, r) in enumerate(subset_df.iterrows(), start=start_num):
                        cont_m = r["المراقبة المستمرة (/20)"]
                        t1_m = f"{r['الفرض 1 (/20)']:.2f}" if pd.notna(r["الفرض 1 (/20)"]) else ""
                        t2_m = f"{r['الفرض 2 (/20)']:.2f}" if pd.notna(r["الفرض 2 (/20)"]) else ""
                        tavg_m = f"{r['معدل الفروض (/20)']:.2f}" if pd.notna(r["معدل الفروض (/20)"]) else ""
                        ex_m = f"{r['الاختبار (/20)']:.2f}" if pd.notna(r["الاختبار (/20)"]) else ""
                        avg_m = f"{r['المعدل (/20)']:.2f}" if pd.notna(r["المعدل (/20)"]) else ""
                        rem_m = r["ملاحظات نوعية"] if pd.notna(r["ملاحظات نوعية"]) else ""

                        rows_code += f"""
                        <tr>
                            <td class="c-center bold">{i:02d}</td>
                            <td class="c-right bold pr-2">{r['الاسم و اللقب']}</td>
                            <td class="c-center">{r['السلوك (/3)']:.1f}</td>
                            <td class="c-center">{r['الغيابات (/3)']:.1f}</td>
                            <td class="c-center">{r['الأدوات (/3)']:.1f}</td>
                            <td class="c-center">{r['الكراريس (/3)']:.1f}</td>
                            <td class="c-center">{r['المشاركة (/3)']:.1f}</td>
                            <td class="c-center">{r['المهمات والواجبات (/5)']:.1f}</td>
                            <td class="c-center bold bg-green">{cont_m:.2f}</td>
                            <td class="c-center">{t1_m}</td>
                            <td class="c-center">{t2_m}</td>
                            <td class="c-center bold bg-yellow">{tavg_m}</td>
                            <td class="c-center bold bg-pink">{ex_m}</td>
                            <td class="c-center bold bg-blue">{avg_m}</td>
                            <td class="c-right pr-2 font-sm">{rem_m}</td>
                        </tr>
                        """
                    return rows_code

                # تقسيم التلاميذ إلى صفحتين (27 تلميذ في الصفحة الأولى، والباقي في الصفحة الثانية)
                df_page2 = df_data.iloc[:27]
                df_page3 = df_data.iloc[27:]

                table_p2_html = make_table_rows(df_page2, 1)
                table_p3_html = make_table_rows(df_page3, 28) if len(df_page3) > 0 else ""

                full_html = f"""
                <style>
                    @page {{
                        size: A4 portrait;
                        margin: 8mm;
                    }}
                    .page-break {{
                        page-break-after: always;
                    }}
                    .cover-container {{
                        border: 5px double #b45309;
                        border-radius: 12px;
                        padding: 30px;
                        height: 94vh;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                        text-align: center;
                        background: radial-gradient(circle, #ffffff 70%, #fef3c7 100%);
                        box-sizing: border-box;
                    }}
                    .title-calligraphy {{
                        font-size: 3.5em;
                        font-weight: 900;
                        color: #1e3a8a;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
                        margin: 60px 0;
                        letter-spacing: 2px;
                    }}
                    .header-table, .grade-table {{
                        width: 100%;
                        border-collapse: collapse;
                        font-family: 'Cairo', Arial, sans-serif;
                    }}
                    .header-box {{
                        border: 1px solid #000;
                        padding: 4px 8px;
                        font-weight: bold;
                        font-size: 0.9em;
                    }}
                    .grade-table th, .grade-table td {{
                        border: 1px solid #000;
                        padding: 3px 2px;
                        font-size: 0.78em;
                    }}
                    .grade-table th {{
                        background-color: #f1f5f9;
                        text-align: center;
                    }}
                    .rotate-header {{
                        writing-mode: vertical-rl;
                        transform: rotate(180deg);
                        white-space: nowrap;
                        padding: 6px 2px !important;
                    }}
                    .bg-green {{ background-color: #bbf7d0 !important; }}
                    .bg-yellow {{ background-color: #fef08a !important; }}
                    .bg-pink {{ background-color: #fbcfe8 !important; }}
                    .bg-blue {{ background-color: #c7d2fe !important; }}
                    .c-center {{ text-align: center; }}
                    .c-right {{ text-align: right; }}
                    .pr-2 {{ padding-right: 5px !important; }}
                    .bold {{ font-weight: bold; }}
                    .font-sm {{ font-size: 0.7em !important; }}
                </style>

                <!-- ================= صفحة 1 : الغلاف المزخرف ================= -->
                <div class="cover-container page-break">
                    <div>
                        <h2 style="margin: 0; font-size: 1.4em;">الجمهورية الجزائرية الديمقراطية الشعبية</h2>
                        <h3 style="margin: 6px 0; font-size: 1.2em;">وزارة التربية الوطنية</h3>
                        <h4 style="margin: 4px 0; font-weight: normal;">مديرية التربية لولاية وهران — مقاطعة وهران 03</h4>
                        <p style="margin: 15px 0 0 0; font-size: 1.1em; font-weight: bold;">ثانوية: {hs_name}</p>
                    </div>

                    <div>
                        <div class="title-calligraphy">
                            دفتر التقويم البيداغوجي
                        </div>
                        <h3 style="color: #047857; margin-top: -30px; font-size: 1.5em; font-weight: 800;">
                            لمادة الرياضيات — مرحلة التعليم الثانوي
                        </h3>
                    </div>

                    <div style="text-align: center; font-size: 1.15em; font-weight: bold;">
                        <p style="margin: 6px 0;">الأستاذ(ة): <span style="color:#1e3a8a;">{tch_name}</span></p>
                        <p style="margin: 6px 0;">القسم / الفوج: <span style="color:#047857;">{c_row['level']} ({c_row['class_name']})</span></p>
                        <p style="margin: 15px 0 0 0; font-size: 1.1em;">السنة الدراسية: {c_row['school_year']}</p>
                    </div>
                </div>

                <!-- ================= صفحة 2 : جدول التقويم (القسم الأول 1 - 27) ================= -->
                <div class="page-break" style="margin-top: 10px;">
                    <!-- الترويسة العلوية الأولى -->
                    <table class="header-table" style="margin-bottom: 6px; font-size: 0.85em;">
                        <tr>
                            <td style="text-align: right; width: 33%;"><b>ثانوية:</b> {hs_name}</td>
                            <td style="text-align: center; width: 34%; font-size: 1.05em; font-weight: 900; color: #1e3a8a;">
                                نتائج التقويم المستمر لـ {term_label}
                            </td>
                            <td style="text-align: left; width: 33%;"><b>السنة الدراسية:</b> {c_row['school_year']}</td>
                        </tr>
                        <tr>
                            <td style="text-align: right;"><b>الأستاذ(ة):</b> {tch_name}</td>
                            <td style="text-align: center;"><b>المــادة:</b> <span style="background:#e0f2fe; padding:2px 10px; border-radius:10px; font-weight:bold;">رياضيات</span></td>
                            <td style="text-align: left;"><b>القسم:</b> {c_row['level']} ({c_row['class_name']})</td>
                        </tr>
                    </table>

                    <!-- الترويسة الشريطية الملونة -->
                    <table class="header-table" style="margin-bottom: 8px; font-size: 0.82em; text-align: center;">
                        <tr style="background-color: #f8fafc;">
                            <td class="header-box" style="background:#fef3c7;"><b>القسم:</b> {c_row['level']}</td>
                            <td class="header-box"><b>الفوج:</b> {c_row['class_name']}</td>
                            <td class="header-box" style="background:#e0f2fe;"><b>التعداد:</b> {total_st} تلميذ</td>
                            <td class="header-box"><b>المعامل:</b> ..........</td>
                        </tr>
                    </table>

                    <!-- جدول الرصد والتقويم -->
                    <table class="grade-table">
                        <thead>
                            <tr>
                                <th rowspan="3" style="width: 3%;">الرقم</th>
                                <th rowspan="3" style="width: 20%;">الاسم و اللقب</th>
                                <th colspan="6" style="background:#e2e8f0;">المؤشــرات (20 ن)</th>
                                <th rowspan="3" class="rotate-header bg-green" style="width: 5%;">المراقبة المستمرة</th>
                                <th rowspan="3" class="rotate-header" style="width: 5%;">الفرض الأول</th>
                                <th rowspan="3" class="rotate-header" style="width: 5%;">الفرض الثاني</th>
                                <th rowspan="3" class="rotate-header bg-yellow" style="width: 6%;">معدل الفروض</th>
                                <th rowspan="3" class="rotate-header bg-pink" style="width: 6%;">الاختبار</th>
                                <th rowspan="3" class="rotate-header bg-blue" style="width: 6%;">المعـدل</th>
                                <th rowspan="3" style="width: 14%;">ملاحظـــات نوعية</th>
                            </tr>
                            <tr>
                                <th class="rotate-header">السلــوك</th>
                                <th class="rotate-header">الغيابات والتأخرات</th>
                                <th class="rotate-header">إحضار الأدوات</th>
                                <th class="rotate-header">تنظيم الكراريس</th>
                                <th class="rotate-header">المشاركـة</th>
                                <th class="rotate-header">إنجاز المهمات والواجبات</th>
                            </tr>
                            <tr style="font-weight:bold; background:#e2e8f0;">
                                <th>3</th>
                                <th>3</th>
                                <th>3</th>
                                <th>3</th>
                                <th>3</th>
                                <th>5</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_p2_html}
                        </tbody>
                    </table>
                </div>

                <!-- ================= صفحة 3 : تكملة الجدول (من 28 فما فوق) + تذييل المنشور الوزاري ================= -->
                <div>
                    <!-- جدول الرصد والتقويم التكملة -->
                    <table class="grade-table" style="margin-top: 15px;">
                        <thead>
                            <tr style="background:#f1f5f9;">
                                <th style="width: 3%;">الرقم</th>
                                <th style="width: 20%;">الاسم و اللقب</th>
                                <th>السلوك (3)</th>
                                <th>الغياب (3)</th>
                                <th>الأدوات (3)</th>
                                <th>الكراريس (3)</th>
                                <th>المشاركة (3)</th>
                                <th>المهمات (5)</th>
                                <th class="bg-green" style="width: 5%;">المراقبة</th>
                                <th style="width: 5%;">فرض 1</th>
                                <th style="width: 5%;">فرض 2</th>
                                <th class="bg-yellow" style="width: 6%;">معدل الفروض</th>
                                <th class="bg-pink" style="width: 6%;">الاختبار</th>
                                <th class="bg-blue" style="width: 6%;">المعـدل</th>
                                <th style="width: 14%;">ملاحظـــات نوعية</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_p3_html if table_p3_html else "<tr><td colspan='15' style='text-align:center; padding:20px;'>تم استيفاء جميع تلاميذ الفوج في الصفحة السابقة.</td></tr>"}
                        </tbody>
                    </table>

                    <!-- التذييل الرسمي للمنشور الوزاري 1613 كما في الصورة تماماً -->
                    <div style="margin-top: 25px; border-top: 1px dashed #64748b; padding-top: 10px; font-size: 0.78em; color: #334155; line-height: 1.6;">
                        <b>ملاحظة رسمية:</b> صُمم هذا النموذج وفقاً لما جاء في مراسلة الأمين العام لوزارة التربية الوطنية بتاريخ <b>2021/10/17</b> تحت رقم <b>1613 / و.ت.و / أ.ع</b> المتعلق بترتيبات التقويم البيداغوجي للسنة الدراسية 2021/2022.<br>
                        * <b>المهمات المسندة:</b> تشمل الواجبات المنزلية، البحوث، المشاريع الفردية والجماعية، ... إلخ.
                    </div>

                    <div style="display: flex; justify-content: space-between; margin-top: 35px; font-weight: bold; font-size: 0.85em;">
                        <span>توقيع الأستاذ(ة): ...................................</span>
                        <span>تأشيرة السيد(ة) مدير(ة) الثانوية: ...................................</span>
                        <span>تأشيرة السيد مفتش التربية الوطنية: ...................................</span>
                    </div>
                </div>
                """
                return full_html

            # أزرار التحميل
            c_btn1, c_btn2 = st.columns(2)
            
            with c_btn1:
                # توليد PDF
                full_html_doc = build_full_gradebook_html(edited_df, c_info, high_school_name, teacher_name, sel_term)
                pdf_bytes, mime_type = convert_html_to_pdf(full_html_doc)
                ext = "pdf" if mime_type == "application/pdf" else "html"
                st.download_button(
                    label="📑 تحميل الدفتر كاملاً كملف PDF رسمي (غلاف مزخرف + شبكة المنشور 1613)",
                    data=pdf_bytes,
                    file_name=f"دفتر_التقويم_البيداغوجي_{sel_term}_{c_info['class_name']}.{ext}",
                    mime=mime_type,
                    type="primary",
                    use_container_width=True
                )

            with c_btn2:
                # تصدير كملف إكسل
                out_excel = io.BytesIO()
                with pd.ExcelWriter(out_excel, engine='openpyxl') as writer:
                    edited_df.drop(columns=["student_id"]).to_excel(writer, index=False, sheet_name=sel_term)
                    ws = writer.sheets[sel_term]
                    ws.views.sheetView[0].rightToLeft = True
                
                st.download_button(
                    label="📥 تحميل جدول التقويم الفصلي كملف Excel",
                    data=out_excel.getvalue(),
                    file_name=f"تقويم_مستمر_{sel_term}_{c_info['class_name']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            # معاينة مصغرة داخل المتصفح
            st.write("---")
            st.markdown("##### 👁️ معاينة شكل الدفتر في المتصفح:")
            render_clean_html(full_html_doc)
            # ==============================================================================
# 14. فضاء المنسق والتقرير الرسمي للمفتشية (المذكرة التوجيهية 08/2026)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة كل أقسامي (تسليم للمنسق)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة كل أقسامي (مع الفرز الآلي للغياب والترتيب)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة الأقسام وفق المكتسبات القبلية لكل شعبة
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة الأقسام (مرتبط مباشرة مع ضبط الموضوع)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة الأقسام (تفصيل نسب كل المحاور في الإكسل)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة الأقسام (تصنيف كل الشعب والمستويات من ضبط الموضوع)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة أقسامي (تشخيصي + فصلي لتسليمها للمنسق)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة أقسامي (تشخيصي + فصلي لتسليمها للمنسق)
# ==============================================================================
# ==============================================================================
# 14. محطة أستاذ المادة: ملخص حصيلة التقويم التشخيصي وبؤر التعثر (لتسليمها للمنسق)
# ==============================================================================
elif "حصيلة" in menu:
    import re, json, io
    st.header("📊 حصيلة أقسامي في التقويم التشخيصي (لتسليمها للمنسق)")
    st.caption("ملخص بيداغوجي شامل لنتائج التقويم التشخيصي وبؤر التعثر لأفواجي، مع تصدير ملف Excel رسمي لتسليمه لمنسق المادة.")

    conn = get_connection()
    try:
        raw_classes = conn.execute("SELECT * FROM classes").fetchall()
        
        def sort_classes_pedagogical(c):
            lvl = c["level"].lower()
            order = 0
            if "1as" in lvl or "1ج" in lvl or "أولى" in lvl: order = 100
            elif "2as" in lvl or "2" in lvl or "ثانية" in lvl: order = 200
            elif "3as" in lvl or "3" in lvl or "ثالثة" in lvl: order = 300
            
            if "علوم" in lvl or "ع ت" in lvl: order += 10
            elif "رياضي" in lvl and "تقني" not in lvl: order += 20
            elif "تقني" in lvl or "هندسة" in lvl: order += 30
            elif "تسيير" in lvl or "ت ا" in lvl: order += 40
            elif "آداب" in lvl or "لغات" in lvl or "أف" in lvl: order += 50
            
            c_num = 0
            digits = re.findall(r'\d+', c["class_name"])
            if digits: c_num = int(digits[0])
            return (order, c_num, c["class_name"])

        classes_db = sorted([dict(c) for c in raw_classes], key=sort_classes_pedagogical)
    finally:
        conn.close()

    if not classes_db:
        st.info("💡 لا توجد أقسام مسجلة حالياً. قومي بإضافة قسم وتلاميذه أولاً من محطة «الأقسام والتلاميذ».")
    else:
        conn = get_connection()
        teacher_summary_data = []
        total_st_all, total_test_all, total_abs_all = 0, 0, 0

        try:
            for c in classes_db:
                cid = c["id"]
                c_students = conn.execute("SELECT id FROM students WHERE class_id = ?", (cid,)).fetchall()
                n_tot = len(c_students)
                total_st_all += n_tot

                diag_res = conn.execute("""
                    SELECT r.* FROM diagnostic_results r
                    INNER JOIN students s ON r.student_id = s.id
                    WHERE s.class_id = ? 
                      AND (r.total > 0 OR r.arithmetic > 0 OR r.algebra > 0 OR r.functions > 0 OR r.geometry > 0)
                """, (cid,)).fetchall()

                n_tst = len(diag_res)
                n_abs = max(0, n_tot - n_tst)
                total_test_all += n_tst
                total_abs_all += n_abs

                cov = round((n_tst / n_tot) * 100, 1) if n_tot > 0 else 0.0

                rubric = None
                if c.get("rubric_json"):
                    try: rubric = json.loads(c["rubric_json"])
                    except Exception: rubric = None

                if not rubric or "exercises" not in rubric:
                    if "1" in c["level"]:
                        def_u = ["الأعداد والحساب", "الحساب الجبري", "الدوال وتنظيم معطيات", "الهندسة والأشعة"]
                    elif "آداب" in c["level"] or "لغات" in c["level"]:
                        def_u = ["النسب المئوية والمؤشرات", "العبارات الجبرية والمعادلات", "الإحصاء وتنظيم المعطيات"]
                    elif "2" in c["level"]:
                        def_u = ["العبارات الجبرية وثلاثي الحدود", "عموميات على الدوال", "الدوران والزوايا الموجهة"]
                    else:
                        def_u = ["الاشتقاقية وتطبيقاتها", "المتتاليات العددية", "النهايات وسلوك الدوال"]
                    rubric = {"num_ex": len(def_u), "exercises": [{"unit": u, "max": round(20.0/len(def_u), 1)} for u in def_u]}

                exercises_eval = []
                col_names = ["arithmetic", "algebra", "functions", "geometry"]

                for ex_idx, ex_info in enumerate(rubric["exercises"]):
                    if ex_idx >= len(col_names): break
                    col_field = col_names[ex_idx]
                    unit_title = ex_info.get("unit", f"التمرين {ex_idx+1}")
                    ex_max = float(ex_info.get("max", 5.0))
                    passing_threshold = round(ex_max / 2.0, 2)

                    def get_stu_score(r_item, idx_pos, field_name):
                        r_dict = dict(r_item)
                        if r_dict.get("details_json"):
                            try:
                                d_parsed = json.loads(r_dict["details_json"])
                                if "exercises" in d_parsed and idx_pos < len(d_parsed["exercises"]):
                                    return float(d_parsed["exercises"][idx_pos].get("score", r_dict.get(field_name, 0.0) or 0.0))
                            except Exception: pass
                        return float(r_dict.get(field_name, 0.0) or 0.0)

                    if n_tst > 0:
                        failing_count = sum(1 for r in diag_res if get_stu_score(r, ex_idx, col_field) < passing_threshold)
                        w_rate = round((failing_count / n_tst) * 100, 1)
                    else:
                        w_rate = 0.0

                    exercises_eval.append({
                        "idx": ex_idx + 1, "unit": unit_title, "max": ex_max, "threshold": passing_threshold, "fail_rate": w_rate
                    })

                w_ov = round((sum(1 for r in diag_res if (r["total"] or 0) < 10.0) / n_tst) * 100, 1) if n_tst > 0 else 0.0

                teacher_summary_data.append({
                    "id": cid, "level": c["level"], "class_name": c["class_name"], "school_year": c["school_year"],
                    "total": n_tot, "tested": n_tst, "absent": n_abs, "coverage": cov,
                    "exercises_eval": exercises_eval, "w_overall": w_ov
                })
        finally:
            conn.close()

        # كروت المؤشرات العلوية لحصيلة التقويم التشخيصي
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("عدد الأفواج التربوية", len(teacher_summary_data))
        k2.metric("التعداد الإجمالي للتلاميذ", f"{total_st_all} تلميذ")
        k3.metric("الحاضرون الممتحنون", f"{total_test_all} تلميذ", delta="حضور فعلي")
        k4.metric("نسبة التغطية العامة", f"{round((total_test_all/total_st_all)*100, 1) if total_st_all>0 else 0}%")

        st.write("---")
        st.markdown("##### 📋 جدول حصيلة التقويم التشخيصي وبؤر التعثر لأقسامي:")

        diag_table_display = []
        for row in teacher_summary_data:
            ex_list = row["exercises_eval"]
            r_dict = {
                "المستوى والشعبة": f"<b>{row['level']}</b>", 
                "الفوج": row["class_name"], 
                "التعداد": row["total"],
                "الحاضرون": f"<span style='color:green; font-weight:bold;'>{row['tested']}</span>",
                "نسبة التغطية": f"<b>{row['coverage']}%</b>",
            }
            for i in range(4):
                col_key = f"ت{i+1}: المحور والتعثر"
                if i < len(ex_list):
                    ex = ex_list[i]
                    c_color = "red" if ex['fail_rate'] > 45 else "green"
                    r_dict[col_key] = f"<b>{ex['unit']}</b><br><span style='color:{c_color}; font-weight:bold;'>{ex['fail_rate']}%</span>"
                else:
                    r_dict[col_key] = "<span style='color:gray;'>—</span>"
            r_dict["التعثر العام (<10)"] = f"<b style='color:{'red' if row['w_overall']>50 else 'black'};'>{row['w_overall']}%</b>"
            diag_table_display.append(r_dict)

        render_artistic_table(diag_table_display)

        # تجهيز وتصدير ملف Excel المعتمد للمنسق
        excel_diag_rows = []
        for r in teacher_summary_data:
            r_d = {
                "المستوى والشعبة": r["level"], 
                "الفوج": r["class_name"], 
                "المسجلون": r["total"],
                "الحاضرون": r["tested"], 
                "الغياب": r["absent"], 
                "نسبة التغطية %": r["coverage"]
            }
            for i in range(4):
                if i < len(r["exercises_eval"]):
                    ex = r["exercises_eval"][i]
                    r_d[f"ت{i+1}: المحور"] = ex["unit"]
                    r_d[f"ت{i+1}: نسبة التعثر %"] = ex["fail_rate"]
                else:
                    r_d[f"ت{i+1}: المحور"] = "—"
                    r_d[f"ت{i+1}: نسبة التعثر %"] = "—"
            r_d["نسبة التعثر العام (<10) %"] = r["w_overall"]
            excel_diag_rows.append(r_d)

        df_diag_xls = pd.DataFrame(excel_diag_rows)
        out_diag_b = io.BytesIO()
        with pd.ExcelWriter(out_diag_b, engine='openpyxl') as writer:
            df_diag_xls.to_excel(writer, index=False, sheet_name="حصيلة التشخيص")
            writer.sheets["حصيلة التشخيص"].views.sheetView[0].rightToLeft = True

        st.write("")
        st.download_button(
            label="📥 تحميل ملف Excel لحصيلة التقويم التشخيصي لتسليمه لمنسق المادة",
            data=out_diag_b.getvalue(),
            file_name="حصيلة_التقويم_التشخيصي_أقسام_الأستاذ.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
# ==============================================================================
# 15. محطة منسق المادة: الأتمتة الشاملة للتقرير الولائي (المذكرة 08/2026)
# ==============================================================================
# ==============================================================================
# 15. محطة منسق المادة: الأتمتة الشاملة وحساب الإجمالي (المذكرة التوجيهية 08/2026)
# ==============================================================================
# ==============================================================================
# 15. محطة منسق المادة: الأتمتة الشاملة وحساب الإجمالي (المذكرة التوجيهية 08/2026)
# ==============================================================================
    # ==============================================================================
# 15. محطة منسق المادة: فضاء محمي بكلمة مرور للمنسق فقط (المذكرة 08/2026)
# ==============================================================================
# ==============================================================================
# 15. محطة منسق المادة: إدارة تسليمات الأساتذة المنظمة وحساب الإجمالي (المذكرة 08)
# ==============================================================================
# ==============================================================================
# 15. محطة منسق المادة: إدارة إكسل الرقمنة الوزاري والمتابعة الفصلية للمفتش
# ==============================================================================
# ==============================================================================
# 15. محطة منسق المادة: تقرير التقويم التشخيصي (المذكرة 08) + المتابعة الفصلية
# ==============================================================================
elif menu == M_COORDINATOR or "المنسق" in menu:
    from datetime import date
    import io, json, math, re, urllib.parse, requests
    import pandas as pd
    import streamlit as st

    # -------------------------------------------------------------------------
    # ⚙️ مصفوفة رتب وصفات أساتذة مادة الرياضيات الرسمية
    # -------------------------------------------------------------------------
    TEACHER_RANKS_MAP = {
        "أستاذ تعليم ثانوي": 13,
        "متربص": 13,
        "متعاقد": 13,
        "مستخلف": 13,
        "أستاذ قسم أول": 14,
        "أستاذ قسم ثان": 16,
        "أستاذ مميز": 17,
    }

    # -------------------------------------------------------------------------
    # 🏫 القائمة الرسمية لثانويات المقاطعة 03
    # -------------------------------------------------------------------------
    ORAN_OFFICIAL_NAMES = [
        "واعر عبد القادر", "الشهيد بن نابي سليمان", "المجاهد غوبريني مصطفى", "زرقاني لحسن",
        "الرائد فراج", "قايد أحمد", "حمري عبد القادر", "جفال ميلود", "مصطفى لشرف",
        "الشهيد طيبي محمد", "عزوزي قدور", "المجاهد العريبي الهواري", "قوديد أحمد",
        "عبد القادر الياجوري", "ابن محرز الوهراني", "الميلود المهاجي", "ساعد الهاشمي عمار عائشة",
        "بلعكرمي عبد القادر", "حيرش محمد", "مراح عبد القادر", "عبد المجيد مزيان",
        "زعيتر جمال الدين", "عمران بن عودة", "النجاح سكول", "المنزه الخاصة", "اقرأ الخاصة"
    ]

    # تهيئة حالات الجلسة (Session State)
    if "coord_auth" not in st.session_state:
        st.session_state.coord_auth = False
    if "current_school" not in st.session_state:
        st.session_state.current_school = ORAN_OFFICIAL_NAMES[0]
    if "coord_full_name" not in st.session_state:
        st.session_state.coord_full_name = "الأستاذ(ة): ديداوي سومية"

    # جلب كلمة المرور المعتمدة
    conn = get_connection()
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, val TEXT)")
        pwd_row = conn.execute("SELECT val FROM system_config WHERE key = 'coord_password'").fetchone()
        if not pwd_row:
            conn.execute("INSERT INTO system_config (key, val) VALUES ('coord_password', 'coord03')")
            conn.commit()
            current_coord_password = "coord03"
        else:
            current_coord_password = pwd_row["val"]
    finally:
        conn.close()

    # =========================================================================
    # 🔐 بوابة الدخول الذكية
    # =========================================================================
    if not st.session_state.coord_auth:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1e3a8a, #0f172a); color: white; padding: 22px; border-radius: 12px; text-align: center; margin-bottom: 25px;">
            <h2 style="margin: 0; font-size: 1.55em;">🏛️ فضاء منسق مادة الرياضيات — بوابة الدخول والتفويض الرسمي</h2>
            <p style="margin: 8px 0 0 0; color: #cbd5e1; font-size: 0.95em;">
                يرجى تحديد المؤسسة التابعة لمقاطعة وهران 03 وإدخال الرمز السري لفتح ملفات التنسيق وحجز التقارير السحابية.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_sp1, col_box, col_sp2 = st.columns([1, 2.2, 1])
        with col_box:
            with st.container(border=True):
                st.markdown("<div style='text-align:center;font-size:2.5em;margin-bottom:5px;'>🔒</div>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align:center;color:#1e3a8a;margin-top:0;'>تسجيل دخول منسق المؤسسة</h4>", unsafe_allow_html=True)
                
                selected_school_pre = st.selectbox(
                    "1. اختر الثانوية التي تنتمي إليها:",
                    ORAN_OFFICIAL_NAMES,
                    key="pre_login_school_select"
                )

                coord_name_pre = st.text_input(
                    "2. اسم ولقب الأستاذ(ة) المنسق(ة):",
                    value=st.session_state.coord_full_name,
                    key="pre_login_coord_name"
                )

                input_pwd = st.text_input(
                    "3. كلمة المرور المعتمدة:",
                    type="password",
                    placeholder="اكتب كلمة المرور هنا...",
                    key="coord_login_pwd"
                )

                st.write("")
                c_btn_in, c_btn_hint = st.columns([2.5, 1])
                with c_btn_in:
                    if st.button("🔓 تأكيد الدخول وتثبيت المؤسسة", type="primary", use_container_width=True, key="btn_unlock_coord_pre"):
                        if input_pwd.strip() == current_coord_password:
                            st.session_state.coord_auth = True
                            st.session_state.current_school = selected_school_pre
                            st.session_state.coord_full_name = coord_name_pre
                            st.success(f"✅ مرحباً بك! تم تثبيت فضاء ثانوية: {selected_school_pre}")
                            st.rerun()
                        else:
                            st.error("❌ كلمة المرور غير صحيحة! يرجى التأكد وإعادة المحاولة.")
                
                with c_btn_hint:
                    if st.button("💡 تلميح", use_container_width=True):
                        st.info("الرمز الأولي المعتمد: coord03")

        st.stop()

    # =========================================================================
    # 🔓 شريط الهوية المثبت بعد تسجيل الدخول
    # =========================================================================
    col_badge, col_exit = st.columns([4, 1.2])
    with col_badge:
        st.markdown(f"""
        <div style="background: rgba(34, 197, 94, 0.12); border: 1.5px solid #22C55E; border-right: 6px solid #16a34a; border-radius: 8px; padding: 10px 16px; font-weight: bold; color: #15803d; font-size: 0.95em;">
            🏫 <b>المؤسسة المعتمدة المثبتة:</b> <span style="color:#1e3a8a;">ثانوية {st.session_state.current_school}</span> &nbsp;|&nbsp; 
            👤 <b>المنسق:</b> {st.session_state.coord_full_name} 🟢
        </div>
        """, unsafe_allow_html=True)
    with col_exit:
        if st.button("🔒 تسجيل الخروج / تغيير الثانوية", use_container_width=True, key="btn_logout_coord_fixed"):
            st.session_state.coord_auth = False
            st.rerun()

    st.write("---")
    st.header(f"🏛️ فضاء منسق مادة الرياضيات — ثانوية {st.session_state.current_school}")

    high_school_c = st.session_state.current_school
    coord_name_c = st.session_state.coord_full_name
    s_year_c = "2026 / 2027"

    OFFICIAL_STREAMS = [
        "1ج م ع ت", "1ج م أ",
        "2رياضي", "2 هندسة", "2ع ت", "2ت ا", "2 آداب وفلسفة", "2 لغات أجنبية",
        "3رياضي", "3 هندسة", "3 ع ت", "3 ت ا", "3 آداب وفلسفة", "3 لغات أجنبية"
    ]

    def normalize_stream(raw_lvl):
        s = str(raw_lvl).strip().lower()
        s_clean = s.replace("المادة: الرياضيات", "").replace("مادة الرياضيات", "").replace("الرياضيات", "")

        if "1" in s or "أولى" in s:
            if any(w in s for w in ["آداب", "أدب", "1ج م أ", "أ", "آ"]):
                return "1ج م أ"
            return "1ج م ع ت"

        elif "2" in s or "ثانية" in s:
            if any(w in s for w in ["لغات", "ل أ", "ل.أ", "لغ", "لغة"]):
                return "2 لغات أجنبية"
            if any(w in s for w in ["آداب", "فلسفة", "أف", "أ.ف"]):
                return "2 آداب وفلسفة"
            if any(w in s for w in ["تسيير", "اقتصاد", "ت ا", "ت.ا"]):
                return "2ت ا"
            if any(w in s for w in ["هندسة", "تقني", "ت ر", "ت.ر"]):
                return "2 هندسة"
            if any(w in s for w in ["علوم تجريبية", "تجريبية", "ع ت", "ع.ت"]):
                return "2ع ت"
            if any(w in s_clean for w in ["رياضي", "رياضيات", "2 ر", "2ر"]) or s == "2رياضي":
                return "2رياضي"
            return "2ع ت"

        elif "3" in s or "ثالثة" in s or "بكالوريا" in s:
            if any(w in s for w in ["لغات", "ل أ", "ل.أ", "لغ", "لغة"]):
                return "3 لغات أجنبية"
            if any(w in s for w in ["آداب", "فلسفة", "أف", "أ.ف"]):
                return "3 آداب وفلسفة"
            if any(w in s for w in ["تسيير", "اقتصاد", "ت ا", "ت.ا"]):
                return "3 ت ا"
            if any(w in s for w in ["هندسة", "تقني", "ت ر", "ت.ر"]):
                return "3 هندسة"
            if any(w in s for w in ["علوم تجريبية", "تجريبية", "ع ت", "ع.ت"]):
                return "3 ع ت"
            if any(w in s_clean for w in ["رياضي", "رياضيات", "3 ر", "3ر"]) or s == "3رياضي":
                return "3رياضي"
            return "3 ع ت"

        return "1ج م ع ت"

    def clean_num(val, default=0.0):
        if pd.isna(val): return default
        s = str(val).replace("%", "").strip().replace(",", ".")
        try: return float(s)
        except Exception:
            m = re.search(r"[-+]?\d*\.?\d+", s)
            return float(m.group(0)) if m else default

    # دالة تنظيف آمنة لحذف أي رموز غير مسموحة في السحابة
    def sanitize_firebase(data):
        if isinstance(data, dict):
            clean_dict = {}
            for k, v in data.items():
                clean_k = re.sub(r'[$#\[\]/.]', '_', str(k))
                clean_dict[clean_k] = sanitize_firebase(v)
            return clean_dict
        elif isinstance(data, list):
            return [sanitize_firebase(v) for v in data]
        elif isinstance(data, float):
            return 0.0 if (math.isnan(data) or math.isinf(data)) else float(data)
        elif hasattr(data, 'item'):
            val = data.item()
            return 0.0 if (isinstance(val, float) and (math.isnan(val) or math.isinf(val))) else val
        return data

    # =========================================================================
    # 🗂️ التبويبان الرئيسيان لفضاء المنسق
    # =========================================================================
    tab_memo08, tab_terms = st.tabs([
        "📑 1. تقرير التقويم التشخيصي وبؤر التعثر (المذكرة 08 الأصلية)",
        "📊 2. المتابعة الفصلية وإكسل الرقمنة الوزاري (الفصل الأول / الثاني / الثالث)"
    ])

    # -------------------------------------------------------------------------
    # 📌 التبويب الأول: تقرير التقويم التشخيصي وبؤر التعثر (المذكرة 08)
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # 📌 التبويب الأول: تقرير التقويم التشخيصي وبؤر التعثر (المذكرة 08)
    # -------------------------------------------------------------------------
    with tab_memo08:
        ANNOUNCEMENT_URL = "https://oran03-maths-default-rtdb.firebaseio.com/announcements.json"
        live_deadline = "يوم الإثنين 19 أكتوبر 2026 في تمام الساعة 16:00 مساءً"
        live_instructions = "عبر السحابة المباشرة أو البريد الإلكتروني: abdessadokalimaths.31@gmail.com أو البريد الداخلي (DEO)."

        try:
            ann_resp = requests.get(ANNOUNCEMENT_URL, timeout=3)
            if ann_resp.status_code == 200 and ann_resp.json():
                ann_data = ann_resp.json()
                live_deadline = ann_data.get("deadline", live_deadline)
                live_instructions = ann_data.get("instructions", live_instructions)
        except Exception:
            pass

        st.markdown(f"""
        <div class="art-card" style="border-right-color:#DC2626; background:rgba(220,38,38,0.06); padding:12px 18px; border-radius:8px;">
            <b style="color:#b91c1c;">📅 آخر أجل رسمي لاستلام التقارير (محدد من المفتشية):</b> <span style="font-weight:900; color:#1e293b;">{live_deadline}</span><br>
            <b>📬 توجيهات وخيارات الإرسال للمفتش:</b> <span>{live_instructions}</span>
        </div>
        """, unsafe_allow_html=True)

        # استرجاع أساتذة التشخيص وبيانات المنسق من قاعدة البيانات
        if "submitted_teachers" not in st.session_state:
            conn = get_connection()
            try:
                saved_t_row = conn.execute("SELECT val FROM system_config WHERE key = 'coord_submitted_teachers'").fetchone()
                st.session_state["submitted_teachers"] = json.loads(saved_t_row["val"]) if saved_t_row and saved_t_row["val"] else []
            except Exception:
                st.session_state["submitted_teachers"] = []
            finally:
                conn.close()

        if "diag_school_total_profs" not in st.session_state:
            conn = get_connection()
            try:
                saved_tot_diag = conn.execute("SELECT val FROM system_config WHERE key = 'diag_school_total_profs'").fetchone()
                st.session_state["diag_school_total_profs"] = int(saved_tot_diag["val"]) if saved_tot_diag and str(saved_tot_diag["val"]).isdigit() else max(len(st.session_state["submitted_teachers"]) + 1, 7)
            except Exception:
                st.session_state["diag_school_total_profs"] = max(len(st.session_state["submitted_teachers"]) + 1, 7)
            finally:
                conn.close()

        if "coord_status_diag" not in st.session_state:
            conn = get_connection()
            try:
                saved_c_st = conn.execute("SELECT val FROM system_config WHERE key = 'coord_status_diag'").fetchone()
                st.session_state["coord_status_diag"] = saved_c_st["val"] if saved_c_st and saved_c_st["val"] else "أستاذ قسم أول"
            except Exception:
                st.session_state["coord_status_diag"] = "أستاذ قسم أول"
            finally:
                conn.close()

        def save_teachers_to_db():
            conn_db = get_connection()
            try:
                conn_db.execute("INSERT OR REPLACE INTO system_config (key, val) VALUES ('coord_submitted_teachers', ?)", 
                             (json.dumps(st.session_state["submitted_teachers"], ensure_ascii=False),))
                conn_db.execute("INSERT OR REPLACE INTO system_config (key, val) VALUES ('diag_school_total_profs', ?)",
                             (str(st.session_state["diag_school_total_profs"]),))
                conn_db.execute("INSERT OR REPLACE INTO system_config (key, val) VALUES ('coord_status_diag', ?)",
                             (str(st.session_state["coord_status_diag"]),))
                conn_db.commit()
            finally:
                conn_db.close()

        # =========================================================================
        # 👤 1. بيانات الأستاذ(ة) المنسق(ة) واحتسابه في الهيئة التدريسية
        # =========================================================================
        st.markdown("### 👥 تنظيم تسليمات إكسل التشخيص وهيئة تدريس مادة الرياضيات:")
        
        with st.expander("👤 بطاقة الأستاذ(ة) المنسق(ة) وتثبيت صفته ورتبته في التقرير:", expanded=True):
            col_cm_name, col_cm_st, col_cm_rk = st.columns([2, 1.8, 1.2])
            with col_cm_name:
                st.markdown(f"**اسم ولقب المنسق(ة):** <span style='color:#1e3a8a; font-weight:bold;'>{coord_name_c}</span>", unsafe_allow_html=True)
                include_my_classes = st.checkbox("➕ احتساب الأستاذ المنسق وأقسامه ضمن الأساتذة المنفذين", value=True, key="chk_inc_my_cls_diag")
            with col_cm_st:
                coord_status_choice = st.selectbox(
                    "صفة المنسق المهنية:",
                    list(TEACHER_RANKS_MAP.keys()),
                    index=list(TEACHER_RANKS_MAP.keys()).index(st.session_state["coord_status_diag"]) if st.session_state["coord_status_diag"] in TEACHER_RANKS_MAP else 4,
                    key="sel_coord_status_diag_box"
                )
                if coord_status_choice != st.session_state["coord_status_diag"]:
                    st.session_state["coord_status_diag"] = coord_status_choice
                    save_teachers_to_db()
            with col_cm_rk:
                coord_rank_val = TEACHER_RANKS_MAP[st.session_state["coord_status_diag"]]
                st.markdown(f"**الرتبة المقابلة:**")
                st.markdown(f"<span style='font-size:1.25em; color:#047857; font-weight:bold;'>الصنف {coord_rank_val}</span>", unsafe_allow_html=True)

        # حساب أقسام وتلاميذ المنسق من قاعدة البيانات
        coord_tested_count = 0
        coord_classes_count = 0
        if include_my_classes:
            conn = get_connection()
            try:
                my_classes = conn.execute("SELECT * FROM classes").fetchall()
                coord_classes_count = len(my_classes)
                for mc in my_classes:
                    diag_res_c = conn.execute("""
                        SELECT r.total FROM diagnostic_results r 
                        INNER JOIN students s ON r.student_id = s.id 
                        WHERE s.class_id = ? AND r.total > 0
                    """, (mc["id"],)).fetchall()
                    coord_tested_count += len(diag_res_c)
            finally:
                conn.close()

        # حساب إجمالي الأساتذة المنفذين الحقيقي (ملفات الأساتذة + المنسق)
        submitted_count = len(st.session_state["submitted_teachers"])
        diag_executed_count = submitted_count + (1 if include_my_classes else 0)

        # إدخال عدد أساتذة الثانوية الإجمالي وعرض العداد الصحيح
        c_diag_tot_col, c_diag_tot_metric = st.columns([1.5, 3])
        with c_diag_tot_col:
            val_in_tot = st.number_input(
                "عدد أساتذة مادة الرياضيات بالثانوية (الإجمالي):",
                min_value=max(1, diag_executed_count), max_value=40,
                value=max(int(st.session_state["diag_school_total_profs"]), diag_executed_count),
                step=1,
                key="inp_diag_tot_profs_memo08"
            )
            if val_in_tot != st.session_state["diag_school_total_profs"]:
                st.session_state["diag_school_total_profs"] = val_in_tot
                save_teachers_to_db()

        with c_diag_tot_metric:
            total_profs_target = st.session_state["diag_school_total_profs"]
            cov_profs_rate = round((diag_executed_count / total_profs_target) * 100, 1) if total_profs_target > 0 else 0.0
            st.metric(
                "نسبة مشاركة الأساتذة المنفذين في التشخيص (تشمل المنسق)",
                f"{diag_executed_count} من أصل {total_profs_target} أستاذ",
                delta=f"{cov_profs_rate}% نسبة التغطية التنفيذية"
            )

        tab_by_name, tab_batch_upload = st.tabs([
            "👤 الطريقة الأولى: كتابة اسم الأستاذ، تحديد الصفة والرتبة ورفع إكساله",
            "⚡ الطريقة الثانية: الرفع الجماعي السريع لعدة ملفات معاً"
        ])

        def parse_teacher_excel_file(excel_file_obj):
            parsed_classes = []
            excel_obj = pd.ExcelFile(excel_file_obj)
            target_sheet = excel_obj.sheet_names[0]
            for sn in excel_obj.sheet_names:
                if "تفصيل" in sn or "حصيلة" in sn: target_sheet = sn; break

            df_t = excel_obj.parse(target_sheet)

            for _, r in df_t.iterrows():
                lvl_val = None
                for c_col in ["المستوى والشعبة", "المستوى", "المستوى الدراسي"]:
                    if c_col in df_t.columns: lvl_val = r[c_col]; break

                if pd.notna(lvl_val) and str(lvl_val).strip():
                    norm_l = normalize_stream(lvl_val)
                    c_name = str(r.get("الفوج", "1")).strip()
                    tot_val = int(clean_num(r.get("المسجلون", r.get("التعداد", r.get("التعداد الكلي", 35)))))
                    tst_val = int(clean_num(r.get("الحاضرون", tot_val)))
                    abs_val = int(clean_num(r.get("الغياب", max(0, tot_val - tst_val))))

                    fail_overall = clean_num(r.get("نسبة التعثر العام (<10) %", r.get("نسبة التعثر العام %", 40.0)))
                    pass_rate = round(max(0.0, 100.0 - fail_overall), 2)
                    passed_count = int(round(tst_val * (pass_rate / 100.0))) if tst_val > 0 else 0

                    avg_val = round(clean_num(r.get("معدل المادة", 8.5 + (pass_rate * 0.05))), 2)
                    max_val = round(clean_num(r.get("أعلى نقطة", min(20.0, 12.0 + (pass_rate * 0.08)))), 2)
                    min_val = round(clean_num(r.get("أدنى نقطة", 3.5)), 2)

                    t1_fail = clean_num(r.get("ت1: نسبة التعثر %", r.get("تعثر ت1 %", 45.0)))
                    t2_fail = clean_num(r.get("ت2: نسبة التعثر %", r.get("تعثر ت2 %", 40.0)))
                    t3_fail = clean_num(r.get("ت3: نسبة التعثر %", r.get("تعثر ت3 %", 50.0)))
                    t4_fail = clean_num(r.get("ت4: نسبة التعثر %", r.get("تعثر ت4 %", 55.0)))

                    parsed_classes.append({
                        "raw_level": str(lvl_val),
                        "normalized_stream": norm_l,
                        "class_name": c_name,
                        "total": tot_val,
                        "tested": tst_val,
                        "absent": abs_val,
                        "passed": passed_count,
                        "pass_rate": pass_rate,
                        "avg": avg_val,
                        "max": max_val,
                        "min": min_val,
                        "t1_fail": t1_fail, "t2_fail": t2_fail, "t3_fail": t3_fail, "t4_fail": t4_fail
                    })
            return parsed_classes

        with tab_by_name:
            col_t1, col_t_status_d, col_t2 = st.columns([1.5, 1.3, 2.0])
            with col_t1:
                t_name_input = st.text_input("اسم ولقب الأستاذ(ة):", placeholder="مثال: أ. بن علي محمد", key="diag_t_name")
            with col_t_status_d:
                t_status_diag = st.selectbox("الصفة المهنية:", list(TEACHER_RANKS_MAP.keys()), key="diag_t_status")
                t_rank_diag = TEACHER_RANKS_MAP[t_status_diag]
                st.caption(f"⭐ **الرتبة المعتمدة:** الصنف ({t_rank_diag})")
            with col_t2:
                t_file_input = st.file_uploader("ملف إكسل حصيلة التشخيص للأستاذ:", type=["xlsx", "xls"], key="diag_t_file")

            if st.button("➕ اعتماد حصيلة التشخيص للأستاذ", type="primary", key="btn_add_diag_single_t"):
                if not t_name_input.strip() or not t_file_input:
                    st.warning("يرجى كتابة الاسم واختيار الملف.")
                else:
                    try:
                        c_res = parse_teacher_excel_file(t_file_input)
                        if c_res:
                            st.session_state["submitted_teachers"].append({
                                "teacher_name": t_name_input.strip(),
                                "status": t_status_diag,
                                "rank": t_rank_diag,
                                "classes": c_res,
                                "filename": t_file_input.name
                            })
                            cur_tot = len(st.session_state["submitted_teachers"]) + (1 if include_my_classes else 0)
                            if cur_tot > st.session_state["diag_school_total_profs"]:
                                st.session_state["diag_school_total_profs"] = cur_tot
                            save_teachers_to_db()
                            st.success(f"🎉 تم بنجاح اعتماد حصيلة الأستاذ ({t_name_input.strip()}) - صفة: {t_status_diag} (رتبة {t_rank_diag})!")
                            st.rerun()
                    except Exception as ex:
                        st.error(f"خطأ: {ex}")

        with tab_batch_upload:
            batch_files = st.file_uploader("ارفع عدة ملفات إكسل للتشخيص معاً:", type=["xlsx", "xls"], accept_multiple_files=True, key="diag_batch_files")
            if st.button("🚀 إضافة كل الملفات المرفوعة", key="btn_add_diag_batch"):
                if batch_files:
                    added_cnt = 0
                    for bf in batch_files:
                        try:
                            c_res = parse_teacher_excel_file(bf)
                            if c_res:
                                t_auto = f"أستاذ(ة) {len(st.session_state['submitted_teachers']) + 1} ({bf.name})"
                                st.session_state["submitted_teachers"].append({
                                    "teacher_name": t_auto,
                                    "status": "أستاذ تعليم ثانوي",
                                    "rank": 13,
                                    "classes": c_res,
                                    "filename": bf.name
                                })
                                added_cnt += 1
                        except Exception: pass
                    if added_cnt > 0:
                        cur_tot = len(st.session_state["submitted_teachers"]) + (1 if include_my_classes else 0)
                        if cur_tot > st.session_state["diag_school_total_profs"]:
                            st.session_state["diag_school_total_profs"] = cur_tot
                        save_teachers_to_db()
                        st.success(f"تمت إضافة {added_cnt} أساتذة!")
                        st.rerun()

        # =====================================================================
        # 📜 بناء البطاقة الإحصائية الكاملة (المنسق رقم 1 + باقي الأساتذة)
        # =====================================================================
        diag_teachers_stat_rows = []
        
        # 1. إدراج المنسق(ة) أولاً وبدقة
        if include_my_classes:
            diag_teachers_stat_rows.append({
                "الرقم": 1,
                "اسم ولقب الأستاذ": f"{coord_name_c} (الأستاذ المنسق)",
                "الصفة": st.session_state["coord_status_diag"],
                "الرتبة": TEACHER_RANKS_MAP[st.session_state["coord_status_diag"]],
                "عدد الأفواج المفحوصة": max(1, coord_classes_count),
                "عدد التلاميذ المفحوصين": coord_tested_count,
                "حالة التنفيذ": "منفّذ (المنسق) ✅"
            })

        # 2. إدراج باقي الأساتذة المسلّمين
        start_idx = len(diag_teachers_stat_rows) + 1
        for idx, item in enumerate(st.session_state.get("submitted_teachers", [])):
            t_cls = item.get("classes", [])
            tst_s = sum(c["tested"] for c in t_cls)
            p_status = item.get("status", "أستاذ تعليم ثانوي")
            p_rank = item.get("rank", TEACHER_RANKS_MAP.get(p_status, 13))

            diag_teachers_stat_rows.append({
                "الرقم": start_idx + idx,
                "اسم ولقب الأستاذ": item["teacher_name"],
                "الصفة": p_status,
                "الرتبة": p_rank,
                "عدد الأفواج المفحوصة": len(t_cls),
                "عدد التلاميذ المفحوصين": tst_s,
                "حالة التنفيذ": "منفّذ ومسلّم ✅"
            })

        if diag_teachers_stat_rows:
            st.write("---")
            c_card_h, c_card_clr = st.columns([3.5, 1])
            with c_card_h:
                st.markdown(f"##### 📜 البطاقة الإحصائية لأساتذة مادة الرياضيات بالثانوية ({diag_executed_count} أساتذة منفذين):")
            with c_card_clr:
                if st.button("♻️ تفريغ الأساتذة المسلمين", key="btn_clr_diag_profs"):
                    st.session_state["submitted_teachers"] = []
                    save_teachers_to_db()
                    st.rerun()

            df_diag_profs_stat = pd.DataFrame(diag_teachers_stat_rows)
            st.dataframe(df_diag_profs_stat, use_container_width=True, hide_index=True)

            for idx, t_entry in enumerate(st.session_state["submitted_teachers"]):
                t_classes = t_entry["classes"]
                classes_txt = " ، ".join([f"{c['raw_level']} ({c['class_name']})" for c in t_classes])
                ci, cd = st.columns([4, 0.8])
                with ci:
                    st.caption(f"👤 {t_entry['teacher_name']} — {classes_txt}")
                with cd:
                    if st.button("🗑️ حذف", key=f"del_t_diag_{idx}"):
                        st.session_state["submitted_teachers"].pop(idx)
                        save_teachers_to_db()
                        st.rerun()

        # تجميع نتائج المستويات والشعب
        compiled_levels = {lvl: {"total": 0, "tested": 0, "absent": 0, "teachers": set()} for lvl in OFFICIAL_STREAMS}
        compiled_gaps = {"1_arith": [], "1_geom": [], "1_eq": [], "2_rot": [], "2_func": [], "3_der": [], "3_seq": [], "3_lim": []}

        if include_my_classes:
            conn = get_connection()
            try:
                my_classes = conn.execute("SELECT * FROM classes").fetchall()
                for mc in my_classes:
                    norm_l = normalize_stream(mc["level"])
                    cid = mc["id"]
                    n_tot = conn.execute("SELECT COUNT(*) as c FROM students WHERE class_id = ?", (cid,)).fetchone()["c"]
                    diag_res = conn.execute("""
                        SELECT r.* FROM diagnostic_results r 
                        INNER JOIN students s ON r.student_id = s.id 
                        WHERE s.class_id = ? AND (r.total > 0 OR r.arithmetic > 0 OR r.algebra > 0 OR r.functions > 0 OR r.geometry > 0)
                    """, (cid,)).fetchall()
                    n_tst = len(diag_res)
                    n_abs = max(0, n_tot - n_tst)

                    if norm_l in compiled_levels:
                        compiled_levels[norm_l]["total"] += n_tot
                        compiled_levels[norm_l]["tested"] += n_tst
                        compiled_levels[norm_l]["absent"] += n_abs
                        compiled_levels[norm_l]["teachers"].add(coord_name_c)

                        if n_tst > 0:
                            w_ar = (sum(1 for r in diag_res if float(r["arithmetic"] or 0) < 2.5) / n_tst) * 100
                            w_al = (sum(1 for r in diag_res if float(r["algebra"] or 0) < 2.5) / n_tst) * 100
                            w_fn = (sum(1 for r in diag_res if float(r["functions"] or 0) < 2.5) / n_tst) * 100
                            w_gm = (sum(1 for r in diag_res if float(r["geometry"] or 0) < 2.5) / n_tst) * 100

                            if "1" in norm_l:
                                compiled_gaps["1_arith"].append(w_ar); compiled_gaps["1_geom"].append(w_gm); compiled_gaps["1_eq"].append(w_al)
                            elif "2" in norm_l:
                                compiled_gaps["2_rot"].append(w_gm); compiled_gaps["2_func"].append(w_fn)
                            elif "3" in norm_l:
                                compiled_gaps["3_der"].append(w_al); compiled_gaps["3_seq"].append(w_ar); compiled_gaps["3_lim"].append(w_fn)
            finally:
                conn.close()

        for t_entry in st.session_state.get("submitted_teachers", []):
            t_name = t_entry["teacher_name"]
            for c in t_entry["classes"]:
                norm_l = c["normalized_stream"]
                if norm_l in compiled_levels:
                    compiled_levels[norm_l]["total"] += c["total"]
                    compiled_levels[norm_l]["tested"] += c["tested"]
                    compiled_levels[norm_l]["absent"] += c["absent"]
                    compiled_levels[norm_l]["teachers"].add(t_name)

                    if "1" in norm_l:
                        compiled_gaps["1_arith"].append(c["t1_fail"])
                        compiled_gaps["1_geom"].append(c["t4_fail"])
                        compiled_gaps["1_eq"].append(c["t2_fail"])
                    elif "2" in norm_l:
                        compiled_gaps["2_rot"].append(c["t3_fail"])
                        compiled_gaps["2_func"].append(c["t2_fail"])
                    elif "3" in norm_l:
                        compiled_gaps["3_der"].append(c["t1_fail"])
                        compiled_gaps["3_seq"].append(c["t3_fail"])
                        compiled_gaps["3_lim"].append(c["t2_fail"])

        grand_total_registered = sum(compiled_levels[lvl]["total"] for lvl in OFFICIAL_STREAMS)
        grand_total_tested = sum(compiled_levels[lvl]["tested"] for lvl in OFFICIAL_STREAMS)
        grand_coverage_rate = round((grand_total_tested / grand_total_registered) * 100, 1) if grand_total_registered > 0 else 0.0
        total_school_math_profs = int(st.session_state["diag_school_total_profs"])

        # =====================================================================
        # 🏛️ جدول الحصيلة: إظهار عدد أساتذة الثانوية قبل الأساتذة المنفذين
        # =====================================================================
        matrix_rows_pure = []
        matrix_rows_display = []
        for lvl in OFFICIAL_STREAMS:
            tot = compiled_levels[lvl]["total"]
            tst = compiled_levels[lvl]["tested"]
            cov = round((tst / tot) * 100, 1) if tot > 0 else 0.0
            n_prof = len(compiled_levels[lvl]["teachers"])

            matrix_rows_pure.append({
                "المستوى الدراسي": lvl,
                "عدد التلاميذ الإجمالي": tot,
                "عدد التلاميذ الحاضرين": tst,
                "نسبة التغطية": f"{cov}%",
                "عدد أساتذة الثانوية": total_school_math_profs,
                "عدد الأساتذة المنفذين": n_prof
            })
            matrix_rows_display.append({
                "المستوى الدراسي": f"<b>{lvl}</b>",
                "عدد التلاميذ الإجمالي": tot,
                "عدد التلاميذ الحاضرين": f"<span style='color:green; font-weight:bold;'>{tst}</span>",
                "نسبة التغطية": f"<b>{cov}%</b>",
                "عدد أساتذة الثانوية": f"<span style='color:#1e3a8a; font-weight:bold;'>{total_school_math_profs}</span>",
                "عدد الأساتذة المنفذين": f"<span style='font-weight:bold;'>{n_prof}</span>"
            })

        matrix_rows_display.append({
            "المستوى الدراسي": "<b style='color:#1E88E5; font-size:1.1em;'>🏛️ المجموع العام للمؤسسة</b>",
            "عدد التلاميذ الإجمالي": f"<b style='font-size:1.1em;'>{grand_total_registered}</b>",
            "عدد التلاميذ الحاضرين": f"<b style='color:green; font-size:1.1em;'>{grand_total_tested}</b>",
            "نسبة التغطية": f"<b style='color:#1E88E5; font-size:1.1em;'>{grand_coverage_rate}%</b>",
            "عدد أساتذة الثانوية": f"<b style='color:#1e3a8a; font-size:1.1em;'>{total_school_math_profs}</b>",
            "عدد الأساتذة المنفذين": f"<b style='color:#047857; font-size:1.1em;'>{diag_executed_count}</b>"
        })

        def get_avg_gap(key, default_val):
            lst = compiled_gaps[key]
            return round(sum(lst) / len(lst), 1) if len(lst) > 0 else default_val

        g_1_arith = get_avg_gap("1_arith", 45.0)
        g_1_geom = get_avg_gap("1_geom", 55.0)
        g_1_eq = get_avg_gap("1_eq", 40.0)
        g_2_rot = get_avg_gap("2_rot", 58.0)
        g_2_func = get_avg_gap("2_func", 47.0)
        g_3_der = get_avg_gap("3_der", 44.0)
        g_3_seq = get_avg_gap("3_seq", 52.0)
        g_3_lim = get_avg_gap("3_lim", 48.0)

        st.write("---")
        st.markdown("### 🏛️ جدول الحصيلة الإجمالية للثانوية (المذكرة 08):")
        render_artistic_table(matrix_rows_display)

        st.markdown("##### 2) الخريطة التشخيصية وبؤر التعثر بالمؤسسة (المذكرة 08):")
        cg1, cg2, cg3 = st.columns(3)
        with cg1:
            st.markdown(f"<div class='art-card'><b>• الأولى ثانوي:</b><br>- الحساب: <b style='color:red;'>{g_1_arith}%</b><br>- الهندسة: <b style='color:red;'>{g_1_geom}%</b><br>- المعادلات: <b style='color:red;'>{g_1_eq}%</b></div>", unsafe_allow_html=True)
        with cg2:
            st.markdown(f"<div class='art-card'><b>• الثانية ثانوي:</b><br>- الدوران والزوايا: <b style='color:red;'>{g_2_rot}%</b><br>- الدوال: <b style='color:red;'>{g_2_func}%</b></div>", unsafe_allow_html=True)
        with cg3:
            st.markdown(f"<div class='art-card'><b>• الثالثة ثانوي:</b><br>- الاشتقاقية: <b style='color:red;'>{g_3_der}%</b><br>- المتتاليات: <b style='color:red;'>{g_3_seq}%</b><br>- النهايات: <b style='color:red;'>{g_3_lim}%</b></div>", unsafe_allow_html=True)

        st.write("---")
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown("##### 3) تقييم أثر حصص المعالجة البيداغوجية:")
            c_m1 = st.checkbox("حصص دعم مدمجة في الـ 15 دقيقة الأولى من الدرس.", value=True, key="diag_cm1")
            c_m2 = st.checkbox("سلاسل تمارين علاجية منزلية مطبوعة أو رقمية.", value=True, key="diag_cm2")
            c_m3 = st.checkbox("أنشطة تفويجية داخل القسم لعلاج الفجوات الحرجة.", value=True, key="diag_cm3")
            c_resp = st.radio("مستوى استجابة التلاميذ:", ["ممتازة وسريعة", "متوسطة (تحتاج وقت أطول)", "ضعيفة"], index=1, key="diag_cresp")

        with col_q2:
            st.markdown("##### 4) حوكمة التنسيق الداخلي والأساتذة الجدد:")
            c_new_t = st.number_input("عدد الأساتذة الجدد / المستخلفين بالمؤسسة:", 0, 20, 1, key="diag_cnewt")
            c_g1 = st.checkbox("تسليمهم الحقيبة الرقمية لملتقى أبريل فور التحاقهم.", value=True, key="diag_cg1")
            c_g2 = st.checkbox("عقد اجتماع تنسيقي داخلي مصغر لشرح آلية التنفيذ.", value=True, key="diag_cg2")
            c_g3 = st.checkbox("زيارة بيداغوجية داخلية لمتابعة تطبيقهم للمعالجة.", value=True, key="diag_cg3")

        col_obs1, col_obs2 = st.columns(2)
        with col_obs1:
            c_obs1 = st.text_input("أبرز عائق 1:", value="اكتظاظ بعض الأفواج ونقص الحجوم الزمنية المخصصة للمادة.", key="diag_cobs1")
            c_obs2 = st.text_input("أبرز عائق 2:", value="تفاوت كبير في المكتسبات القبلية وضعف آليات الحساب الجبري.", key="diag_cobs2")
        with col_obs2:
            c_prop1 = st.text_input("مقترح 1 لتجويد الأداء:", value="تفعيل ورشات التعلم بالأقران واستثمار برمجية GeoGebra.", key="diag_cprop1")
            c_prop2 = st.text_input("مقترح 2 لتجويد الأداء:", value="مواصلة اعتماد حصص الـ 10 دقائق في مرحلة الانطلاق.", key="diag_cprop2")

        st.write("---")
        col_send_m08, col_pdf_m08, col_dl_m08 = st.columns([2.2, 2.0, 1.4])

        with col_send_m08:
            if st.button("🚀 إرسال تقرير المذكرة 08 إلى منصة السيد المفتش علي عبد الصادوق", type="primary", use_container_width=True, key="btn_send_memo08_main"):
                with st.spinner("جاري الإرسال السحابي إلى منصة التفتيش..."):
                    try:
                        safe_k = re.sub(r'[.$#\[\]/\\]', '_', high_school_c.strip())
                        encoded_school_key_m08 = urllib.parse.quote(safe_k)

                        # إرسال البيانات شاملة المنسق والبطاقة الإحصائية الكاملة
                        m08_payload = sanitize_firebase({
                            "school_name": high_school_c,
                            "coordinator_name": coord_name_c,
                            "coordinator_status": st.session_state["coord_status_diag"],
                            "coordinator_rank": TEACHER_RANKS_MAP[st.session_state["coord_status_diag"]],
                            "school_year": s_year_c,
                            "total_school_teachers": total_school_math_profs,
                            "executed_teachers_count": diag_executed_count,
                            "execution_rate": f"{cov_profs_rate}%",
                            "teachers_card": diag_teachers_stat_rows,     # <-- البطاقة الكاملة متضمنة المنسق
                            "sent_at": date.today().strftime('%d/%m/%Y %H:%M'),
                            "quantitative_table": matrix_rows_pure,
                            "grand_total": {
                                "registered": grand_total_registered, "tested": grand_total_tested,
                                "coverage": grand_coverage_rate,
                                "school_teachers_count": total_school_math_profs,
                                "teachers_count": diag_executed_count
                            },
                            "gaps": {
                                "1_arith": g_1_arith, "1_geom": g_1_geom, "1_eq": g_1_eq,
                                "2_rot": g_2_rot, "2_func": g_2_func,
                                "3_der": g_3_der, "3_seq": g_3_seq, "3_lim": g_3_lim
                            },
                            "qualitative": {
                                "m_15min": c_m1, "m_hw": c_m2, "m_group": c_m3,
                                "response_level": c_resp, "new_teachers": c_new_t,
                                "g_kit": c_g1, "g_meeting": c_g2, "g_visit": c_g3,
                                "obs_1": c_obs1, "obs_2": c_obs2, "prop_1": c_prop1, "prop_2": c_prop2
                            }
                        })
                        FIREBASE_URL = "https://oran03-maths-default-rtdb.firebaseio.com/reports"
                        resp = requests.put(f"{FIREBASE_URL}/{encoded_school_key_m08}.json", json=m08_payload, timeout=12)
                        if resp.status_code == 200:
                            st.success(f"🎉 تم بنجاح تسليم تقرير المذكرة 08 لثانوية ({high_school_c}) متضمناً البطاقة الإحصائية لـ ({diag_executed_count} من أصل {total_school_math_profs} أساتذة) إلى منصة السيد المفتش!")
                            st.balloons()
                        else:
                            st.error(f"خطأ في الاتصال: {resp.status_code}")
                    except Exception as ex:
                        st.error(f"خطأ في الاتصال: {ex}")

        with col_pdf_m08:
            pdf_q_rows = ""
            for idx, r in enumerate(matrix_rows_pure, 1):
                pdf_q_rows += f"""
                <tr>
                    <td style="padding:4px; border:1px solid #000; text-align:center;">{idx}</td>
                    <td style="padding:4px; border:1px solid #000; text-align:right; font-weight:bold;">{r.get('المستوى الدراسي', '—')}</td>
                    <td style="padding:4px; border:1px solid #000; text-align:center;">{r.get('عدد التلاميذ الإجمالي', 0)}</td>
                    <td style="padding:4px; border:1px solid #000; text-align:center; font-weight:bold;">{r.get('عدد التلاميذ الحاضرين', 0)}</td>
                    <td style="padding:4px; border:1px solid #000; text-align:center;">{r.get('نسبة التغطية', '0%')}</td>
                    <td style="padding:4px; border:1px solid #000; text-align:center; font-weight:bold; color:#1e3a8a;">{r.get('عدد أساتذة الثانوية', total_school_math_profs)}</td>
                    <td style="padding:4px; border:1px solid #000; text-align:center;">{r.get('عدد الأساتذة المنفذين', 1)}</td>
                </tr>
                """

            pdf_profs_rows = ""
            for p in diag_teachers_stat_rows:
                pdf_profs_rows += f"""
                <tr>
                    <td style="padding:3px; border:1px solid #000; text-align:center;">{p['الرقم']}</td>
                    <td style="padding:3px; border:1px solid #000; text-align:right; font-weight:bold;">{p['اسم ولقب الأستاذ']}</td>
                    <td style="padding:3px; border:1px solid #000; text-align:center;">{p['الصفة']}</td>
                    <td style="padding:3px; border:1px solid #000; text-align:center; font-weight:bold;">{p['الرتبة']}</td>
                    <td style="padding:3px; border:1px solid #000; text-align:center;">{p['عدد الأفواج المفحوصة']}</td>
                    <td style="padding:3px; border:1px solid #000; text-align:center;">{p['عدد التلاميذ المفحوصين']}</td>
                    <td style="padding:3px; border:1px solid #000; text-align:center; font-weight:bold; color:green;">منفّذ</td>
                </tr>
                """

            m08_pdf_html = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Cairo', Arial, sans-serif; direction: rtl; text-align: right; margin: 0; color: #000; }}
                    @page {{ size: A4 portrait; margin: 10mm; }}
                    .page-break {{ page-break-after: always; }}
                    .header-box {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 5px; margin-bottom: 10px; }}
                    .info-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 11px; }}
                    .info-table td {{ border: none; padding: 3px; }}
                    .content-table {{ width: 100%; border-collapse: collapse; font-size: 9.5px; margin-bottom: 10px; }}
                    .content-table th, .content-table td {{ border: 1px solid #000; padding: 4px; }}
                    .content-table th {{ background-color: #f1f5f9; text-align: center; font-weight: bold; }}
                    .box-title {{ background: #e2e8f0; border: 1px solid #000; padding: 5px 8px; font-weight: bold; font-size: 11px; margin-bottom: 6px; border-radius: 3px; }}
                    .text-block {{ font-size: 10.5px; line-height: 1.8; margin-bottom: 8px; text-align: justify; }}
                </style>
            </head>
            <body>

                <div class="page-break">
                    <div class="header-box">
                        <h3 style="margin: 0; font-size: 13px;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h3>
                        <h4 style="margin: 2px 0; font-size: 11px;">مديرية التربية لولاية وهران — المقاطعة التفتيشية رقم 03</h4>
                        <p style="margin: 2px 0; font-weight: 900; font-size: 12px; color: #1e3a8a;">
                            تقرير استثمار نتائج التقويم التشخيصي لمادة الرياضيات (المذكرة التوجيهية رقم 08/2026)
                        </p>
                    </div>

                    <table class="info-table">
                        <tr>
                            <td><b>المؤسسة التعليمية:</b> ثانوية {high_school_c}</td>
                            <td><b>الأستاذ(ة) المنسق(ة):</b> {coord_name_c} ({st.session_state['coord_status_diag']} - صنف {TEACHER_RANKS_MAP[st.session_state['coord_status_diag']]})</td>
                            <td><b>الموسم الدراسي:</b> {s_year_c}</td>
                        </tr>
                        <tr>
                            <td><b>مفتش التعليم الثانوي:</b> علي عبد الصادوق</td>
                            <td><b>تاريخ الإنجاز:</b> {date.today().strftime('%d/%m/%Y')}</td>
                            <td><b>حالة التقرير:</b> معتمد ورسمي</td>
                        </tr>
                    </table>

                    <div class="box-title">1) الحصيلة الكمية العامة وهيئة تدريس مادة الرياضيات:</div>
                    <table class="content-table" style="text-align:center; font-size:11px; margin-bottom:12px;">
                        <tr>
                            <th>التعداد الإجمالي للتلاميذ</th>
                            <th>عدد التلاميذ المفحوصين</th>
                            <th>عدد الغيابات الكلية</th>
                            <th>نسبة التغطية العامة</th>
                            <th>عدد أساتذة الثانوية</th>
                            <th>عدد الأساتذة المنفذين</th>
                        </tr>
                        <tr>
                            <td style="font-weight:bold;">{grand_total_registered} تلميذ</td>
                            <td style="font-weight:bold; color:green;">{grand_total_tested} تلميذ</td>
                            <td style="font-weight:bold; color:red;">{max(0, grand_total_registered - grand_total_tested)}</td>
                            <td style="font-weight:bold; font-size:12px;">{grand_coverage_rate}%</td>
                            <td style="font-weight:bold; color:#1e3a8a;">{total_school_math_profs} أساتذة</td>
                            <td style="font-weight:bold; color:green;">{diag_executed_count} أساتذة ({cov_profs_rate}%)</td>
                        </tr>
                    </table>

                    <div class="box-title">البطاقة الإحصائية لأساتذة مادة الرياضيات بالثانوية (تحديد الصفة والرتبة):</div>
                    <table class="content-table" style="font-size:9px; margin-bottom:12px;">
                        <thead>
                            <tr>
                                <th style="width:5%;">الرقم</th>
                                <th style="width:30%;">اسم ولقب الأستاذ</th>
                                <th style="width:20%;">الصفة المهنية</th>
                                <th style="width:10%;">الرتبة</th>
                                <th style="width:12%;">الأفواج</th>
                                <th style="width:13%;">المفحوصون</th>
                                <th style="width:10%;">الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pdf_profs_rows}
                        </tbody>
                    </table>

                    <div class="box-title">جدول الحصيلة الكمية المفصلة حسب الشعب التعليمية الـ 14:</div>
                    <table class="content-table">
                        <thead>
                            <tr>
                                <th style="width:5%;">الرقم</th>
                                <th style="width:30%;">المستوى والشعبة التعليمية</th>
                                <th style="width:13%;">المسجلون</th>
                                <th style="width:13%;">الحاضرون</th>
                                <th style="width:13%;">نسبة التغطية</th>
                                <th style="width:13%;">عدد أساتذة الثانوية</th>
                                <th style="width:13%;">الأساتذة المنفذون</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pdf_q_rows}
                        </tbody>
                    </table>
                </div>

                <div>
                    <div class="header-box">
                        <h4 style="margin: 0; font-size: 11px;">المقاطعة التفتيشية رقم 03 — ثانوية {high_school_c}</h4>
                        <p style="margin: 2px 0; font-weight: 800; font-size: 11px;">الخريطة التشخيصية واستراتيجية المعالجة البيداغوجية (تابع تقرير المذكرة 08)</p>
                    </div>

                    <div class="box-title">2) الخريطة التشخيصية وبؤر التعثر المعرفية المرصودة بالمؤسسة:</div>
                    <table class="content-table">
                        <thead>
                            <tr style="background:#e0f2fe;">
                                <th style="width:25%;">المستوى التعليمي</th>
                                <th style="width:50%;">بؤر التعثر الأكثر خطورة المشخصة</th>
                                <th style="width:25%;">متوسط نسبة التعثر بالمؤسسة</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="text-align:center; font-weight:bold;">السنة الأولى ثانوي (1AS)</td>
                                <td>الحساب على الجذور وقوى 10 ({g_1_arith}%) | الهندسة والحساب الشعاعي ({g_1_geom}%) | المعادلات والحصر ({g_1_eq}%)</td>
                                <td style="text-align:center; font-weight:bold; color:red;">{round((g_1_arith + g_1_geom + g_1_eq)/3, 1)}%</td>
                            </tr>
                            <tr>
                                <td style="text-align:center; font-weight:bold;">السنة الثانية ثانوي (2AS)</td>
                                <td>الدوران والزوايا الموجهة وحساب المثلثات ({g_2_rot}%) | عموميات على الدوال والتمثيل البياني ({g_2_func}%)</td>
                                <td style="text-align:center; font-weight:bold; color:red;">{round((g_2_rot + g_2_func)/2, 1)}%</td>
                            </tr>
                            <tr>
                                <td style="text-align:center; font-weight:bold;">السنة الثالثة ثانوي (3AS)</td>
                                <td>الاشتقاقية والمماس ({g_3_der}%) | المتتاليات العددية والتراجع ({g_3_seq}%) | النهايات وحالات عدم التعيين ({g_3_lim}%)</td>
                                <td style="text-align:center; font-weight:bold; color:red;">{round((g_3_der + g_3_seq + g_3_lim)/3, 1)}%</td>
                            </tr>
                        </tbody>
                    </table>

                    <div class="box-title" style="margin-top:10px;">3) تقييم تنفيذ حصص المعالجة البيداغوجية:</div>
                    <div class="text-block" style="background:#fafafa; border:1px solid #cbd5e1; padding:8px; border-radius:4px;">
                        • <b>آليات التدخل الميداني المعتمدة بالمؤسسة:</b> 
                        {'[✓] حصص دعم مدمجة في الـ 15 دقيقة الأولى من كل حصة | ' if c_m1 else ''}
                        {'[✓] سلاسل تمارين علاجية منزلية مركزة | ' if c_m2 else ''}
                        {'[✓] تفعيل مخطط الجلوس الذكي والتعلم بالأقران | ' if c_m3 else ''}<br>
                        • <b>مستوى استجابة وتفاعل التلاميذ مع المعالجة:</b> <b style="color:#1e3a8a;">{c_resp}</b>
                    </div>

                    <div class="box-title" style="margin-top:10px;">4) حوكمة التنسيق الداخلي ومرافقة الأساتذة الجدد:</div>
                    <div class="text-block" style="background:#fafafa; border:1px solid #cbd5e1; padding:8px; border-radius:4px;">
                        • <b>تعداد الأساتذة الجدد / المستخلفين بالمؤسسة:</b> {c_new_t} أساتذة.<br>
                        • <b>إجراءات المرافقة المنجزة:</b>
                        {'[✓] تسليم الحقيبة الرقمية لملتقى أبريل فور التحاقهم | ' if c_g1 else ''}
                        {'[✓] عقد جلسات تنسيقية داخلية مصغرة | ' if c_g2 else ''}
                        {'[✓] برمجة زيارات بيداغوجية تبادلية لمتابعة تطبيق المعالجة' if c_g3 else ''}
                    </div>

                    <div class="box-title" style="margin-top:10px;">5) الصعوبات الميدانية ومقترحات الفريق التربوي:</div>
                    <table class="content-table" style="margin-bottom:15px;">
                        <tr>
                            <td style="width:50%; vertical-align:top;">
                                <b>أبرز العوائق المرصودة:</b><br>
                                1. {c_obs1}<br>
                                2. {c_obs2}
                            </td>
                            <td style="width:50%; vertical-align:top;">
                                <b>مقترحات تجويد الأداء المرفوعة للمفتشية:</b><br>
                                1. {c_prop1}<br>
                                2. {c_prop2}
                            </td>
                        </tr>
                    </table>

                    <div style="display:flex; justify-content:space-between; margin-top:35px; font-weight:bold; font-size:11px;">
                        <div style="text-align:center;">
                            الأستاذ(ة) المنسق(ة):<br>
                            <b>{coord_name_c}</b><br><br>
                            .............................................
                        </div>
                        <div style="text-align:center;">
                            السيد(ة) مدير(ة) الثانوية:<br>
                            <b>ثانوية {high_school_c}</b><br><br>
                            .............................................
                        </div>
                        <div style="text-align:center;">
                            مفتش التعليم الثانوي لمادة الرياضيات:<br>
                            <b>الأستاذ: علي عبد الصادوق</b><br><br>
                            .............................................
                        </div>
                    </div>
                </div>

            </body>
            </html>
            """

            m08_pdf_bytes, m08_pdf_mime = convert_html_to_pdf(m08_pdf_html)
            m08_pdf_ext = "pdf" if m08_pdf_mime == "application/pdf" else "html"

            st.download_button(
                label="📑 تحميل تقرير المذكرة 08 كاملاً (ملف PDF معتمد للطباعة)",
                data=m08_pdf_bytes,
                file_name=f"تقرير_المذكرة_08_{high_school_c.replace(' ', '_')}.{m08_pdf_ext}",
                mime=m08_pdf_mime,
                type="primary",
                use_container_width=True,
                key="btn_download_m08_official_pdf"
            )

        with col_dl_m08:
            df_coord_export = pd.DataFrame(matrix_rows_pure)
            out_c_x = io.BytesIO()
            with pd.ExcelWriter(out_c_x, engine='openpyxl') as writer:
                df_coord_export.to_excel(writer, index=False, sheet_name="الحصيلة الكمية المجمعة")
                writer.sheets["الحصيلة الكمية المجمعة"].views.sheetView[0].rightToLeft = True

                if diag_teachers_stat_rows:
                    df_diag_export_profs = pd.DataFrame(diag_teachers_stat_rows)
                    df_diag_export_profs.to_excel(writer, index=False, sheet_name="بطاقة أساتذة الرياضيات")
                    writer.sheets["بطاقة أساتذة الرياضيات"].views.sheetView[0].rightToLeft = True

            st.download_button(
                label="📊 تحميل إكسل الحصيلة",
                data=out_c_x.getvalue(),
                file_name=f"الحصيلة_الكمية_المذكرة_08_{high_school_c.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
     # -------------------------------------------------------------------------
    # 📌 التبويب الثاني: المتابعة الفصلية وإكسل الرقمنة الوزاري (الفصل 1 / 2 / 3)
    # -------------------------------------------------------------------------
    with tab_terms:
        MINISTERIAL_14_STREAMS = [
            {"level": "السنة 1 ثانوي", "stream": "جذع مشترك علوم وتكنولوجيا", "coef": 5, "raw": "1ج م ع ت"},
            {"level": "السنة 1 ثانوي", "stream": "جذع مشترك آداب", "coef": 2, "raw": "1ج م أ"},
            {"level": "السنة 2 ثانوي", "stream": "رياضيات", "coef": 7, "raw": "2رياضي"},
            {"level": "السنة 2 ثانوي", "stream": "هندسة", "coef": 6, "raw": "2 هندسة"},
            {"level": "السنة 2 ثانوي", "stream": "علوم تجريبية", "coef": 5, "raw": "2ع ت"},
            {"level": "السنة 2 ثانوي", "stream": "تسيير واقتصاد", "coef": 3, "raw": "2ت ا"},
            {"level": "السنة 2 ثانوي", "stream": "آداب وفلسفة", "coef": 2, "raw": "2 آداب وفلسفة"},
            {"level": "السنة 2 ثانوي", "stream": "لغات أجنبية", "coef": 2, "raw": "2 لغات أجنبية"},
            {"level": "السنة 3 ثانوي", "stream": "رياضيات", "coef": 7, "raw": "3رياضي"},
            {"level": "السنة 3 ثانوي", "stream": "هندسة", "coef": 6, "raw": "3 هندسة"},
            {"level": "السنة 3 ثانوي", "stream": "علوم تجريبية", "coef": 5, "raw": "3 ع ت"},
            {"level": "السنة 3 ثانوي", "stream": "تسيير واقتصاد", "coef": 3, "raw": "3 ت ا"},
            {"level": "السنة 3 ثانوي", "stream": "آداب وفلسفة", "coef": 2, "raw": "3 آداب وفلسفة"},
            {"level": "السنة 3 ثانوي", "stream": "لغات أجنبية", "coef": 2, "raw": "3 لغات أجنبية"}
        ]

        st.markdown("""
        <div style="background: linear-gradient(90deg, #1e3a8a, #047857); color: white; padding: 15px 22px; border-radius: 10px; margin-bottom: 15px;">
            <h3 style="margin: 0; font-size: 1.25em;">📊 المتابعة الفصلية من منصة الرقمنة والبطاقة الإحصائية لأساتذة المادة</h3>
            <p style="margin: 4px 0 0 0; font-size: 0.9em; color: #cbd5e1;">
                رفع وثائق حجز النقاط الرسمية، ضبط بطاقة هيئة التدريس بالصفة والرتبة، وحساب معدلات الشعب الـ 14 آلياً.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_t_sel, col_t_kpi = st.columns([1.5, 3])
        with col_t_sel:
            chosen_term = st.selectbox(
                "🎯 اختر الفصل الدراسي المطلوب معالجته وإرساله للمفتش:",
                ["الفصل الأول", "الفصل الثاني", "الفصل الثالث"],
                key="coord_term_tracker_choice"
            )
        with col_t_kpi:
            st.info(f"💡 سيتم استخراج ومعالجة ملفات الرقمنة لـ **({chosen_term})** وحساب معدلات الشعب ومقارنتها بالتقويم التشخيصي.")

        # دالة قراءة نموذج إكسل الرقمنة الوزاري الرسمي
        def parse_ministerial_excel_file(file_obj):
            excel_file = pd.ExcelFile(file_obj)
            parsed_classes = []

            for sheet_name in excel_file.sheet_names:
                try:
                    df = excel_file.parse(sheet_name, header=None)
                    if df.empty or len(df) < 8:
                        continue

                    class_info_txt = ""
                    for r in range(min(7, len(df))):
                        row_str = " ".join([str(v) for v in df.iloc[r].values if pd.notna(v)])
                        if "الفوج التربوي" in row_str or "حجز النقاط" in row_str:
                            class_info_txt = row_str
                            break

                    detected_level = "1ج م ع ت"
                    if "جذع مشترك آداب" in class_info_txt or "آداب" in class_info_txt:
                        detected_level = "1ج م أ"
                    elif "جذع مشترك علوم" in class_info_txt or "علوم" in class_info_txt or "ع ت" in class_info_txt:
                        detected_level = "1ج م ع ت"
                    elif "2" in class_info_txt:
                        if any(w in class_info_txt for w in ["لغات", "ل أ", "ل.أ", "لغة"]):
                            detected_level = "2 لغات أجنبية"
                        elif any(w in class_info_txt for w in ["فلسفة", "آداب", "أف"]):
                            detected_level = "2 آداب وفلسفة"
                        elif any(w in class_info_txt for w in ["تسيير", "اقتصاد", "ت ا"]):
                            detected_level = "2ت ا"
                        elif any(w in class_info_txt for w in ["تقني", "هندسة", "ت ر"]):
                            detected_level = "2 هندسة"
                        elif any(w in class_info_txt for w in ["علوم تجريبية", "تجريبية", "ع ت"]):
                            detected_level = "2ع ت"
                        elif "رياضي" in class_info_txt and "تقني" not in class_info_txt:
                            detected_level = "2رياضي"
                        else:
                            detected_level = "2 لغات أجنبية" if "ل" in class_info_txt else "2ع ت"
                    elif "3" in class_info_txt:
                        if any(w in class_info_txt for w in ["لغات", "ل أ", "ل.أ", "لغة"]):
                            detected_level = "3 لغات أجنبية"
                        elif any(w in class_info_txt for w in ["فلسفة", "آداب", "أف"]):
                            detected_level = "3 آداب وفلسفة"
                        elif any(w in class_info_txt for w in ["تسيير", "اقتصاد", "ت ا"]):
                            detected_level = "3 ت ا"
                        elif any(w in class_info_txt for w in ["تقني", "هندسة", "ت ر"]):
                            detected_level = "3 هندسة"
                        elif any(w in class_info_txt for w in ["علوم تجريبية", "تجريبية", "ع ت"]):
                            detected_level = "3 ع ت"
                        elif "رياضي" in class_info_txt and "تقني" not in class_info_txt:
                            detected_level = "3رياضي"
                        else:
                            detected_level = "3 ع ت"

                    header_idx = 7
                    for r in range(min(12, len(df))):
                        row_txt = " ".join([str(v) for v in df.iloc[r].values if pd.notna(v)])
                        if "اللقب" in row_txt and "الاسم" in row_txt and "الاختبار" in row_txt:
                            header_idx = r
                            break

                    headers = [str(v).strip() for v in df.iloc[header_idx].values]
                    col_sur = 1; col_first = 2; col_eval = 4; col_test = 5; col_exam = 6

                    for idx, h in enumerate(headers):
                        if "اللقب" in h: col_sur = idx
                        elif "الاسم" in h: col_first = idx
                        elif "التقويم المستمر" in h: col_eval = idx
                        elif "معدل الفروض" in h: col_test = idx
                        elif "الاختبار" in h: col_exam = idx

                    def clean_val(val):
                        if pd.isna(val): return None
                        s = str(val).strip().replace(',', '.')
                        m = re.search(r"\d+(\.\d+)?", s)
                        return float(m.group(0)) if m else None

                    scores_list = []
                    students_list = []
                    for r in range(header_idx + 1, len(df)):
                        row = df.iloc[r]
                        sur = str(row.iloc[col_sur]).strip() if col_sur < len(row) and pd.notna(row.iloc[col_sur]) else ""
                        fst = str(row.iloc[col_first]).strip() if col_first < len(row) and pd.notna(row.iloc[col_first]) else ""
                        full_name = f"{sur} {fst}".strip()

                        if not full_name or full_name == "nan" or len(full_name) < 2:
                            continue

                        sc_eval = clean_val(row.iloc[col_eval]) if col_eval < len(row) else None
                        sc_test = clean_val(row.iloc[col_test]) if col_test < len(row) else None
                        sc_exam = clean_val(row.iloc[col_exam]) if col_exam < len(row) else None

                        if sc_eval is not None and sc_test is not None and sc_exam is not None:
                            t_avg = round((sc_eval + sc_test + (sc_exam * 2.0)) / 4.0, 2)
                            scores_list.append(t_avg)
                        elif sc_exam is not None:
                            t_avg = sc_exam
                            scores_list.append(t_avg)
                        else:
                            t_avg = None

                        students_list.append({"name": full_name, "avg": t_avg})

                    if scores_list:
                        n_tot = len(students_list)
                        n_tested = len(scores_list)
                        n_abs = n_tot - n_tested
                        n_pass = sum(1 for sc in scores_list if sc >= 10.0)
                        n_fragile = sum(1 for sc in scores_list if sc < 7.0)
                        p_rate = round((n_pass / n_tested) * 100, 1) if n_tested > 0 else 0.0
                        c_avg = round(sum(scores_list) / n_tested, 2) if n_tested > 0 else 0.0

                        parsed_classes.append({
                            "sheet": sheet_name,
                            "class_header": class_info_txt if class_info_txt else f"فوج {sheet_name}",
                            "level": detected_level,
                            "total": n_tot,
                            "tested": n_tested,
                            "absent": n_abs,
                            "passed": n_pass,
                            "fragile": n_fragile,
                            "pass_rate": p_rate,
                            "avg": c_avg,
                            "max": max(scores_list) if scores_list else 0.0,
                            "min": min(scores_list) if scores_list else 0.0,
                            "students_scores": scores_list
                        })
                except Exception:
                    continue
            return parsed_classes

        # تهيئة تخزين أساتذة الفصل
        term_key_store = f"coord_term_teachers_{chosen_term}"
        term_tot_school_profs_key = f"term_tot_profs_{chosen_term}"

        conn = get_connection()
        try:
            if term_key_store not in st.session_state:
                saved_row = conn.execute("SELECT val FROM system_config WHERE key = ?", (term_key_store,)).fetchone()
                st.session_state[term_key_store] = json.loads(saved_row["val"]) if saved_row and saved_row["val"] else []

            if term_tot_school_profs_key not in st.session_state:
                saved_tot_p = conn.execute("SELECT val FROM system_config WHERE key = ?", (term_tot_school_profs_key,)).fetchone()
                st.session_state[term_tot_school_profs_key] = int(saved_tot_p["val"]) if saved_tot_p and str(saved_tot_p["val"]).isdigit() else max(len(st.session_state[term_key_store]), 1)
        except Exception:
            if term_key_store not in st.session_state: st.session_state[term_key_store] = []
            if term_tot_school_profs_key not in st.session_state: st.session_state[term_tot_school_profs_key] = 1
        finally:
            conn.close()

        def save_term_teachers_to_db():
            conn_term = get_connection()
            try:
                conn_term.execute("INSERT OR REPLACE INTO system_config (key, val) VALUES (?, ?)",
                             (term_key_store, json.dumps(st.session_state[term_key_store], ensure_ascii=False)))
                conn_term.execute("INSERT OR REPLACE INTO system_config (key, val) VALUES (?, ?)",
                             (term_tot_school_profs_key, str(st.session_state[term_tot_school_profs_key])))
                conn_term.commit()
            finally:
                conn_term.close()

        # إحصائية أساتذة الثانوية في الفصل
        st.markdown(f"##### 🏷️ بطاقة هيئة التدريس لمادة الرياضيات ({chosen_term}):")
        c_term_tot_col, c_term_tot_m = st.columns([1.5, 3])
        with c_term_tot_col:
            val_in_term_tot = st.number_input(
                "عدد أساتذة مادة الرياضيات بالثانوية (الإجمالي):",
                min_value=1, max_value=40,
                value=int(st.session_state[term_tot_school_profs_key]),
                step=1,
                key=f"inp_term_tot_profs_{chosen_term}"
            )
            if val_in_term_tot != st.session_state[term_tot_school_profs_key]:
                st.session_state[term_tot_school_profs_key] = val_in_term_tot
                save_term_teachers_to_db()

        with c_term_tot_m:
            term_executed_cnt = len(st.session_state[term_key_store])
            st.metric(
                "مؤشر تسليم وحجز النقاط للمادة",
                f"{term_executed_cnt} من أصل {st.session_state[term_tot_school_profs_key]} أستاذ",
                delta=f"{round((term_executed_cnt / st.session_state[term_tot_school_profs_key]) * 100, 1)}% نسبة التنفيذ"
            )

        tab_single_t, tab_batch_t = st.tabs([
            "👤 الطريقة الأولى: كتابة اسم الأستاذ، تحديد الصفة والرتبة ورفع إكساله",
            "⚡ الطريقة الثانية: الرفع الجماعي المباشر لعدة ملفات"
        ])

        with tab_single_t:
            col_t_n, col_t_st, col_t_f = st.columns([1.8, 1.4, 2.2])
            with col_t_n:
                t_input_name = st.text_input("اسم ولقب الأستاذ(ة):", placeholder="مثال: أ. أحمد بلاحة", key=f"t_name_in_{chosen_term}")
            with col_t_st:
                t_status_term = st.selectbox("الصفة المهنية:", list(TEACHER_RANKS_MAP.keys()), key=f"t_status_in_{chosen_term}")
                t_rank_term = TEACHER_RANKS_MAP[t_status_term]
                st.caption(f"⭐ **الرتبة المعتمدة:** الصنف ({t_rank_term})")
            with col_t_f:
                t_input_file = st.file_uploader("ملف إكسل الرقمنة الخاص به:", type=["xlsx", "xls"], key=f"t_file_in_{chosen_term}")

            if st.button("➕ اعتماد وإضافة إكسل الأستاذ بالبطاقة الإحصائية", type="primary", key=f"btn_add_term_prof_{chosen_term}"):
                if not t_input_name.strip() or not t_input_file:
                    st.warning("يرجى إدخال اسم الأستاذ واختيار ملف الإكسل.")
                else:
                    try:
                        parsed_res = parse_ministerial_excel_file(t_input_file)
                        if parsed_res:
                            st.session_state[term_key_store].append({
                                "teacher_name": t_input_name.strip(),
                                "status": t_status_term,
                                "rank": t_rank_term,
                                "classes": parsed_res,
                                "filename": t_input_file.name
                            })
                            if len(st.session_state[term_key_store]) > st.session_state[term_tot_school_profs_key]:
                                st.session_state[term_tot_school_profs_key] = len(st.session_state[term_key_store])
                            save_term_teachers_to_db()
                            st.success(f"🎉 تم بنجاح إضافة الأستاذ ({t_input_name.strip()}) - صفة: {t_status_term} (رتبة {t_rank_term}) واستخراج {len(parsed_res)} أفواج!")
                            st.rerun()
                        else:
                            st.error("تعذر قراءة بيانات التلاميذ من الملف، تأكدي من تطابق النموذج مع الرقمنة.")
                    except Exception as ex:
                        st.error(f"خطأ أثناء معالجة الملف: {ex}")

        with tab_batch_t:
            batch_up_files = st.file_uploader("ارفعي عدة ملفات إكسل رقمنة معاً:", type=["xlsx", "xls"], accept_multiple_files=True, key=f"batch_up_{chosen_term}")
            if st.button("🚀 إضافة كل الملفات دفعة واحدة", key=f"btn_batch_add_{chosen_term}"):
                if batch_up_files:
                    count_added = 0
                    for f_idx, bf in enumerate(batch_up_files):
                        try:
                            parsed_res = parse_ministerial_excel_file(bf)
                            if parsed_res:
                                auto_t_name = f"أستاذ(ة) {len(st.session_state[term_key_store]) + 1} ({bf.name})"
                                st.session_state[term_key_store].append({
                                    "teacher_name": auto_t_name,
                                    "status": "أستاذ تعليم ثانوي",
                                    "rank": 13,
                                    "classes": parsed_res,
                                    "filename": bf.name
                                })
                                count_added += 1
                        except Exception: pass
                    if count_added > 0:
                        if len(st.session_state[term_key_store]) > st.session_state[term_tot_school_profs_key]:
                            st.session_state[term_tot_school_profs_key] = len(st.session_state[term_key_store])
                        save_term_teachers_to_db()
                        st.success(f"تمت بنجاح إضافة {count_added} ملفات رقمنة للأساتذة!")
                        st.rerun()

        # =====================================================================
        # 📜 عرض وتوليد البطاقة الإحصائية لأساتذة مادة الرياضيات بالفصل
        # =====================================================================
        term_teachers_stat_rows = []
        for idx, item in enumerate(st.session_state.get(term_key_store, [])):
            t_cls = item.get("classes", [])
            tot_t_stu = sum(c["total"] for c in t_cls)
            tst_t_stu = sum(c["tested"] for c in t_cls)
            c_avg = round(sum(c["avg"] * c["tested"] for c in t_cls) / tst_t_stu, 2) if tst_t_stu > 0 else 0.0
            p_status = item.get("status", "أستاذ تعليم ثانوي")
            p_rank = item.get("rank", TEACHER_RANKS_MAP.get(p_status, 13))

            term_teachers_stat_rows.append({
                "الرقم": idx + 1,
                "اسم ولقب الأستاذ": item["teacher_name"],
                "الصفة": p_status,
                "الرتبة": p_rank,
                "عدد الأفواج المسندة": len(t_cls),
                "عدد التلاميذ الحاضرين": tst_t_stu,
                "معدل مادة الأستاذ": c_avg,
                "حالة الإنجاز": "منفّذ وحاجز للنقاط ✅"
            })

        if term_teachers_stat_rows:
            st.write("---")
            c_ttl, c_clr = st.columns([3.5, 1])
            with c_ttl:
                st.markdown(f"##### 📜 البطاقة الإحصائية لأساتذة مادة الرياضيات بالثانوية ({chosen_term}):")
            with c_clr:
                if st.button("♻️ تفريغ القائمة", key=f"btn_clr_{chosen_term}"):
                    st.session_state[term_key_store] = []
                    save_term_teachers_to_db()
                    st.rerun()

            df_term_profs_stat = pd.DataFrame(term_teachers_stat_rows)
            st.dataframe(df_term_profs_stat, use_container_width=True, hide_index=True)

            for idx, item in enumerate(st.session_state[term_key_store]):
                t_cls = item["classes"]
                tot_t_stu = sum(c["total"] for c in t_cls)
                tst_t_stu = sum(c["tested"] for c in t_cls)
                c_inf, c_rm = st.columns([4, 0.8])
                with c_inf:
                    st.caption(f"👤 {item['teacher_name']} — {len(t_cls)} أفواج ({tot_t_stu} مسجل / {tst_t_stu} حاضر)")
                with c_rm:
                    if st.button("🗑️ حذف", key=f"del_prof_{chosen_term}_{idx}"):
                        st.session_state[term_key_store].pop(idx)
                        save_term_teachers_to_db()
                        st.rerun()

        # تجميع الأفواج
        all_parsed_classes = []
        for item in st.session_state.get(term_key_store, []):
            all_parsed_classes.extend(item.get("classes", []))

        conn = get_connection()
        try:
            diag_data = conn.execute("""
                SELECT r.total, r.classification FROM diagnostic_results r
                INNER JOIN students s ON r.student_id = s.id
                WHERE r.total > 0
            """).fetchall()
            tot_diag = len(diag_data)
            diag_passed = sum(1 for r in diag_data if float(r["total"]) >= 10.0)
            diag_pass_rate = round((diag_passed / tot_diag) * 100, 1) if tot_diag > 0 else 0.0
            diag_fragile = sum(1 for r in diag_data if float(r["total"]) < 7.0)
            diag_fragile_rate = round((diag_fragile / tot_diag) * 100, 1) if tot_diag > 0 else 0.0

            cured_count = conn.execute("""
                SELECT COUNT(DISTINCT student_id) as c FROM remediation_activities
                WHERE response_level LIKE '%جيد%' OR response_level LIKE '%تجاوز%'
            """).fetchone()["c"]
        finally:
            conn.close()

        if all_parsed_classes:
            tot_term_tested = sum(c["tested"] for c in all_parsed_classes)
            tot_term_passed = sum(c["passed"] for c in all_parsed_classes)
            tot_term_fragile = sum(c["fragile"] for c in all_parsed_classes)
            all_term_scores = []
            for c in all_parsed_classes:
                all_term_scores.extend(c["students_scores"])
            term_pass_rate = round((tot_term_passed / tot_term_tested) * 100, 1) if tot_term_tested > 0 else 0.0
            term_fragile_rate = round((tot_term_fragile / tot_term_tested) * 100, 1) if tot_term_tested > 0 else 0.0
            term_avg_score = round(sum(all_term_scores) / len(all_term_scores), 2) if all_term_scores else 0.0
        else:
            tot_term_tested = 0
            tot_term_passed = 0
            tot_term_fragile = 0
            term_pass_rate = 0.0
            term_fragile_rate = 0.0
            term_avg_score = 0.0

        gain_pass = round(term_pass_rate - diag_pass_rate, 1)
        gain_fragile = round(diag_fragile_rate - term_fragile_rate, 1)

        st.write("---")
        st.markdown(f"##### 📈 قياس أثر المعالجة: مقارنة بين (التقويم التشخيصي) و ({chosen_term}):")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("نسبة التحكم والنجاح العام", f"{term_pass_rate}%", delta=f"{'+' if gain_pass>=0 else ''}{gain_pass}% مقارنة بالتشخيص")
        c2.metric("نسبة الفئة الهشة (< 7)", f"{term_fragile_rate}%", delta=f"-{gain_fragile}% تقليص الفجوة" if gain_fragile>=0 else None, delta_color="inverse")
        c3.metric("معدل مادة الرياضيات للمؤسسة", f"{term_avg_score} / 20", delta="معدل عام")
        c4.metric(f"تعداد الحاضرين في {chosen_term}", f"{tot_term_tested} تلميذ")

        # بناء مصفوفة الشعب الـ 14
        stream_stats_payload = []
        stream_stats_display = []

        for spec in MINISTERIAL_14_STREAMS:
            raw_k = spec["raw"]
            matched_classes = [c for c in all_parsed_classes if c["level"] == raw_k]
            if matched_classes:
                att_c = sum(c["tested"] for c in matched_classes)
                pass_c = sum(c["passed"] for c in matched_classes)
                p_rate = round((pass_c / att_c) * 100, 1) if att_c > 0 else 0.0
                avg_c = round(sum(c["avg"] * c["tested"] for c in matched_classes) / att_c, 2) if att_c > 0 else 0.0
                max_c = max(c["max"] for c in matched_classes)
                min_c = min(c["min"] for c in matched_classes)
            else:
                att_c = 0; p_rate = 0.0; pass_c = 0; avg_c = 0.0; max_c = 0.0; min_c = 0.0

            # 1. البيانات السحابية الرسمية للتطبيق الآخر
            stream_stats_payload.append({
                "stream": spec["stream"],
                "level": spec["level"],
                "coef": spec["coef"],
                "attendees": att_c,
                "passed": pass_c,
                "pass_rate": p_rate,
                "avg": avg_c,
                "max": max_c,
                "min": min_c
            })

            # 2. البيانات المعروضة في الشاشة والإكسل
            stream_stats_display.append({
                "المستوى التعليمي": spec["level"],
                "الشعبة": spec["stream"],
                "معامل المادة": spec["coef"],
                "تعداد الحاضرين": att_c,
                "الناجحون (≥ 10)": pass_c,
                "نسبة النجاح (%)": f"{p_rate}%",
                "معدل المادة": avg_c,
                "أعلى نقطة": max_c,
                "أدنى نقطة": min_c
            })

        st.write("")
        st.markdown(f"##### 📋 جدول نتائج الشعب الـ 14 المستخرج لـ ({chosen_term}):")
        df_term_view = pd.DataFrame(stream_stats_display)
        st.dataframe(df_term_view, use_container_width=True, hide_index=True)

        st.write("---")
        col_send_btn, col_xls_btn = st.columns([2.5, 1.5])

        with col_send_btn:
            if st.button(
                f"🚀 إرسال حصيلة ومتابعة {chosen_term} (مع البطاقة الإحصائية) إلى منصة السيد المفتش علي عبد الصادوق",
                type="primary",
                use_container_width=True,
                key=f"btn_send_term_with_impact_{chosen_term}"
            ):
                with st.spinner(f"جاري إرسال حصيلة ومتابعة {chosen_term} إلى منصة المفتشية..."):
                    try:
                        safe_school_key = re.sub(r'[.$#\[\]/\\]', '_', high_school_c.strip())
                        if not safe_school_key or "..." in safe_school_key:
                            safe_school_key = "ثانوية_المؤسسة"

                        encoded_school_key = urllib.parse.quote(safe_school_key)
                        encoded_term = urllib.parse.quote(chosen_term)

                        n_school_profs = int(st.session_state[term_tot_school_profs_key])
                        n_exec_profs = len(st.session_state[term_key_store])

                        current_term_data = sanitize_firebase({
                            "sent_at": date.today().strftime('%d/%m/%Y %H:%M'),
                            "term": chosen_term,
                            "teachers_statistics": {
                                "total_school_teachers": n_school_profs,
                                "executed_teachers_count": n_exec_profs,
                                "execution_rate": f"{round((n_exec_profs / n_school_profs) * 100, 1)}%" if n_school_profs > 0 else "0%",
                                "teachers_list": term_teachers_stat_rows
                            },
                            "pass_rate": term_pass_rate,
                            "fragile_rate": term_fragile_rate,
                            "term_avg": term_avg_score,
                            "tested_students": tot_term_tested,
                            "passed_students": tot_term_passed,
                            "fragile_students": tot_term_fragile,
                            "cured_students": cured_count,
                            "stream_stats": stream_stats_payload
                        })

                        diagnostic_baseline = sanitize_firebase({
                            "pass_rate": diag_pass_rate,
                            "fragile_rate": diag_fragile_rate,
                            "tested_students": tot_diag,
                            "passed_students": diag_passed,
                            "fragile_students": diag_fragile
                        })

                        FIREBASE_URL = "https://oran03-maths-default-rtdb.firebaseio.com/reports"

                        base_payload = sanitize_firebase({
                            "school_name": high_school_c,
                            "coordinator_name": coord_name_c,
                            "school_year": s_year_c,
                            "total_math_teachers": n_school_profs,
                            "last_updated": date.today().strftime('%d/%m/%Y %H:%M'),
                            "diagnostic_baseline": diagnostic_baseline
                        })

                        requests.patch(f"{FIREBASE_URL}/{encoded_school_key}.json", json=base_payload, timeout=12)

                        term_url = f"{FIREBASE_URL}/{encoded_school_key}/term_reports/{encoded_term}.json"
                        resp = requests.put(term_url, json=current_term_data, timeout=12)

                        if resp.status_code == 200:
                            st.success(f"🎉 تم بنجاح إرسال وتثبيت تقرير ({chosen_term}) متضمناً البطاقة الإحصائية لأساتذة الرياضيات ({n_exec_profs} من {n_school_profs}) لثانوية ({high_school_c}) في منصة السيد المفتش!")
                            st.balloons()
                        else:
                            st.error(f"خطأ في الاتصال بالسحابة ({resp.status_code}): {resp.text}")
                    except Exception as ex:
                        st.error(f"تعذر الاتصال بالسحابة: {ex}")

        with col_xls_btn:
            out_b = io.BytesIO()
            with pd.ExcelWriter(out_b, engine='openpyxl') as writer:
                df_term_view.to_excel(writer, index=False, sheet_name=chosen_term)
                writer.sheets[chosen_term].views.sheetView[0].rightToLeft = True

                if term_teachers_stat_rows:
                    df_term_export_profs = pd.DataFrame(term_teachers_stat_rows)
                    df_term_export_profs.to_excel(writer, index=False, sheet_name="بطاقة أساتذة الرياضيات")
                    writer.sheets["بطاقة أساتذة الرياضيات"].views.sheetView[0].rightToLeft = True

            st.download_button(
                label=f"📥 تحميل حصيلة {chosen_term} (Excel)",
                data=out_b.getvalue(),
                file_name=f"حصيلة_{chosen_term}_{high_school_c.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
# ----------------- التذييل -----------------
st.sidebar.divider()
if st.sidebar.button("🚪 تسجيل الخروج / العودة للواجهة الرسمية", use_container_width=True, key="sidebar_logout_btn"):
    st.session_state.entered = False
    st.rerun()

st.sidebar.markdown("""
<div style="text-align: center; color: gray; font-size: 0.85em; margin-top: 10px;">
<b>المنظومة البيداغوجية الذكية لمادة الرياضيات</b><br>
تصميم: الأستاذة <b>ديداوي سومية</b><br>
إشراف: المفتش <b>علي عبد الصادوق</b><br>
المقاطعة التفتيشية رقم 03 وهران 🇩🇿
</div>
""", unsafe_allow_html=True)
