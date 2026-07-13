"""
رابط کاربری Streamlit برای سیستم ارزیابی هوشمند پروپوزال‌های فارسی
"""

import streamlit as st
import requests
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# تنظیمات صفحه
st.set_page_config(
    page_title="ارزیابی هوشمند پروپوزال",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS سفارشی - رسمی و اداری، راست‌چین، فونت نازنین
st.markdown("""
<style>
    @font-face {
        font-family: 'B Nazanin';
        src: local('B Nazanin'), local('BNazanin'), local('B_Nazanin');
    }
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

    /* === RTL و فونت سراسری === */
    html, body, [class*="css"] {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', 'Arial', sans-serif !important;
    }
    .stApp, .main .block-container {
        direction: rtl !important;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown h1,
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stText {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', sans-serif !important;
    }
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
    [data-testid="stMetricDelta"] {
        direction: rtl !important;
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', sans-serif !important;
    }

    /* === هدر اصلی === */
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        text-align: center !important;
        color: #ffffff;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #1a3263 0%, #2c5282 100%);
        padding: 1.2rem 1rem;
        border-radius: 0.6rem;
        border-bottom: 4px solid #0f1f3d;
        letter-spacing: 0.5px;
    }

    /* === کارت‌های نمره === */
    .score-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 0.6rem;
        border: 1px solid #d1d5db;
        border-right: 5px solid #1a3263;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }

    /* === باکس‌های وضعیت === */
    .success-box {
        background: #f0fdf4;
        color: #14532d;
        padding: 1rem 1.2rem;
        border-radius: 0.5rem;
        border: 1px solid #a7f3d0;
        border-right: 5px solid #16a34a;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    .warning-box {
        background: #fffbeb;
        color: #78350f;
        padding: 1rem 1.2rem;
        border-radius: 0.5rem;
        border: 1px solid #fcd34d;
        border-right: 5px solid #d97706;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    .error-box {
        background: #fef2f2;
        color: #7f1d1d;
        padding: 1rem 1.2rem;
        border-radius: 0.5rem;
        border: 1px solid #fca5a5;
        border-right: 5px solid #dc2626;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    .high-box {
        background: #fef2f2;
        color: #7f1d1d;
        padding: 1rem 1.2rem;
        border-radius: 0.5rem;
        border: 1px solid #fca5a5;
        border-right: 5px solid #dc2626;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        line-height: 1.8;
    }
    .medium-box {
        background: #fffbeb;
        color: #78350f;
        padding: 1rem 1.2rem;
        border-radius: 0.5rem;
        border: 1px solid #fcd34d;
        border-right: 5px solid #d97706;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
        line-height: 1.8;
    }

    /* === دکمه‌ها === */
    .stButton > button {
        background: linear-gradient(135deg, #1a3263 0%, #2c5282 100%);
        color: #ffffff !important;
        border: none;
        padding: 0.7rem 2rem;
        font-weight: 700;
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', sans-serif !important;
        border-radius: 0.5rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0f1f3d 0%, #1a3263 100%);
        box-shadow: 0 3px 10px rgba(26,50,99,0.3);
    }

    /* === تب‌ها === */
    .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9;
        border: 1px solid #d1d5db;
        border-radius: 0.6rem;
        padding: 0.4rem;
        direction: rtl !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        color: #1a3263;
        font-family: 'B Nazanin', 'Vazirmatn', 'Tahoma', sans-serif !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1a3263 !important;
        color: #ffffff !important;
    }

    /* === وضعیت نهایی === */
    .status-success {
        background: #16a34a;
        color: #ffffff;
        padding: 0.75rem 1.2rem;
        border-radius: 0.5rem;
        font-weight: 700;
        text-align: center !important;
        font-size: 1rem;
    }
    .status-error {
        background: #dc2626;
        color: #ffffff;
        padding: 0.75rem 1.2rem;
        border-radius: 0.5rem;
        font-weight: 700;
        text-align: center !important;
        font-size: 1rem;
    }

    /* === نشانگر پردازش === */
    .processing-indicator {
        background: #f8fafc;
        color: #1e293b;
        padding: 2rem;
        border-radius: 0.6rem;
        border: 1px solid #cbd5e0;
        text-align: center !important;
        margin: 1rem 0;
        direction: rtl !important;
    }
    .processing-indicator ul {
        list-style: none;
        padding: 0;
    }
    .processing-indicator li {
        padding: 0.3rem 0;
    }

    /* === سایدبار === */
    [data-testid="stSidebar"] {
        direction: rtl !important;
        text-align: right !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        direction: rtl !important;
        text-align: right !important;
    }

    /* === جدول === */
    .stDataFrame {
        direction: ltr;
    }

    /* === فوتر === */
    .app-footer {
        text-align: center !important;
        color: #64748b;
        font-size: 0.85rem;
        padding: 1rem;
        border-top: 2px solid #e2e8f0;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# پیکربندی API
API_BASE_URL = st.sidebar.text_input(
    "آدرس API",
    value="http://localhost:8000",
    help="آدرس سرور API"
)

# Header
st.markdown('<div class="main-header">سیستم ارزیابی هوشمند پروپوزال‌های فارسی</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("تنظیمات ارزیابی")
    
    use_llm = st.checkbox("استفاده از تحلیلگر هوشمند", value=True, help="استفاده از مدل زبانی برای تحلیل عمیق محتوا")
    detailed_report = st.checkbox("گزارش جامع", value=True, help="تولید گزارش کامل و تفصیلی")
    
    st.divider()
    
    st.header("اطلاعات سیستم")
    st.info("""
    **معیارهای ارزیابی استاندارد:**
    
    - **نگارش و ساختار** (45%)
    - **محتوای علمی** (35%)
    - **منابع و ارجاعات** (15%)
    - **اصالت و نوآوری** (5%)
    """)
    
    st.divider()
    
    st.header("وضعیت سیستم")
    if st.button("بررسی سلامت سیستم", use_container_width=True):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ سیستم آماده به کار است")
            else:
                st.error("❌ سیستم در دسترس نیست")
        except Exception as e:
            st.error(f"❌ خطا در اتصال: {str(e)}")


# Tab های اصلی
tab1, tab2, tab3 = st.tabs(["ارسال پروپوزال", "نتایج ارزیابی", "راهنمای سیستم"])

# Tab 1: ارزیابی
with tab1:
    st.header("ارسال و ارزیابی پروپوزال")
    
    uploaded_file = st.file_uploader(
        "فایل پروپوزال را انتخاب کنید",
        type=['pdf', 'docx', 'doc'],
        help="فایل‌های PDF و Microsoft Word پشتیبانی می‌شوند (حداکثر 50 مگابایت)"
    )
    
    if uploaded_file is not None:
        # نمایش اطلاعات فایل
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("نام فایل", uploaded_file.name)
        with col2:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.metric("حجم فایل", f"{file_size_mb:.2f} مگابایت")
        with col3:
            file_type = uploaded_file.type or "Unknown"
            st.metric("نوع فایل", file_type.split('/')[-1] if '/' in file_type else file_type)
        
        # دکمه ارزیابی
        if st.button("شروع فرآیند ارزیابی", type="primary", use_container_width=True):
            if file_size_mb > 50:
                st.error("❌ حجم فایل بیش از حد مجاز (50 مگابایت) است!")
            else:
                # نمایش محتوای رسمی به جای بادکنک
                st.markdown("""
                <div class="processing-indicator">
                    <h3>📋 در حال ارزیابی پروپوزال</h3>
                    <p>لطفاً منتظر بمانید. فرآیند ارزیابی شامل مراحل زیر است:</p>
                    <ul style="text-align: right; direction: rtl;">
                        <li>✅ استخراج و پیش‌پردازش متن</li>
                        <li>✅ تحلیل نگارشی و ساختاری</li>
                        <li>✅ تشخیص اصالت و بررسی تقلب</li>
                        <li>✅ تحلیل محتوای علمی</li>
                        <li>✅ محاسبه نمرات نهایی</li>
                        <li>✅ تولید گزارش جامع</li>
                    </ul>
                    <p><strong>زمان تقریبی: 2-5 دقیقه</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.spinner("در حال پردازش..."):
                    try:
                        # ارسال درخواست به API
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        params = {
                            "use_llm": use_llm,
                            "detailed_report": detailed_report
                        }
                        
                        response = requests.post(
                            f"{API_BASE_URL}/api/evaluate",
                            files=files,
                            params=params,
                            timeout=300  # 5 دقیقه
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # ذخیره نتیجه در session state
                            st.session_state['evaluation_result'] = result
                            st.session_state['evaluation_time'] = time.time()
                            
                            # نمایش موفقیت رسمی
                            st.markdown("""
                            <div class="status-success">
                                ✅ ارزیابی پروپوزال با موفقیت انجام شد
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # نمایش خلاصه سریع
                            st.subheader("خلاصه نتایج")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(
                                    "نمره نهایی",
                                    f"{result['final_evaluation']['final_score']:.1f}",
                                    delta=f"درجه: {result['final_evaluation']['grade']}"
                                )
                            with col2:
                                status_text = "قبول" if result['final_evaluation']['pass'] else "رد"
                                st.metric(
                                    "وضعیت",
                                    status_text,
                                )
                            with col3:
                                st.metric(
                                    "سطح کیفی",
                                    result['final_evaluation']['level']
                                )
                            
                            # هدایت به تب نتایج
                            st.info("💡 برای مشاهده گزارش کامل، به تب 'نتایج ارزیابی' مراجعه کنید.")
                            
                        else:
                            error_data = response.json()
                            st.markdown(f"""
                            <div class="status-error">
                                ❌ خطا در ارزیابی: {error_data.get('message', 'خطای نامشخص')}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ زمان ارزیابی به پایان رسید. لطفاً دوباره تلاش کنید.")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 خطا در اتصال به سیستم. لطفاً وضعیت سرور را بررسی کنید.")
                    except Exception as e:
                        st.error(f"❌ خطا: {str(e)}")

# Tab 2: نتایج
with tab2:
    st.header("گزارش کامل ارزیابی")
    
    if 'evaluation_result' not in st.session_state:
        st.info("ℹ️ لطفاً ابتدا یک پروپوزال را برای ارزیابی ارسال کنید.")
    else:
        result = st.session_state['evaluation_result']
        
        # Header با نمره نهایی
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "نمره نهایی",
                f"{result['final_evaluation']['final_score']:.2f}",
                delta=f"درجه: {result['final_evaluation']['grade']}"
            )
        with col2:
            st.metric("درجه کیفی", result['final_evaluation']['grade'])
        with col3:
            st.metric("سطح ارزیابی", result['final_evaluation']['level'])
        with col4:
            status_text = "قبول" if result['final_evaluation']['pass'] else "رد"
            status_class = "status-success" if result['final_evaluation']['pass'] else "status-error"
            st.markdown(f"""
            <div class="{status_class}">
                وضعیت: {status_text}
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # نمرات جزئی
        st.subheader("تحلیل جزئی نمرات")
        
        scores = result['final_evaluation']['individual_scores']
        weights = result['final_evaluation']['weights']
        weighted_scores = result['final_evaluation']['weighted_scores']
        
        # نمودار میله‌ای نمرات
        criterion_names = {
            'writing': 'نگارش و ساختار',
            'structure': 'ساختار پروپوزال',
            'content': 'محتوای علمی',
            'references': 'منابع و ارجاعات',
            'originality': 'اصالت و نوآوری'
        }
        
        df_scores = pd.DataFrame({
            'معیار ارزیابی': [criterion_names.get(k, k) for k in scores.keys()],
            'نمره کسب شده': list(scores.values()),
            'وزن معیار': [f"{weights[k]*100:.0f}%" for k in scores.keys()],
            'نمره وزن‌دار': list(weighted_scores.values())
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            # نمودار میله‌ای
            fig = px.bar(
                df_scores,
                x='معیار ارزیابی',
                y='نمره کسب شده',
                color='نمره کسب شده',
                color_continuous_scale='RdYlGn',
                title='نمودار تحلیل نمرات',
                labels={'نمره کسب شده': 'نمره (0-100)'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # جدول نمرات
            st.dataframe(
                df_scores,
                use_container_width=True,
                hide_index=True
            )
        
        st.divider()
        
        # تحلیل نقاط قوت و ضعف
        st.subheader("تحلیل کیفی پروپوزال")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ نقاط قوت")
            if result['analysis']['strengths']:
                for i, strength in enumerate(result['analysis']['strengths'], 1):
                    st.markdown(f"<div class='success-box'>{i}. {strength}</div>", unsafe_allow_html=True)
            else:
                st.info("نقطه قوت خاصی شناسایی نشد.")
        
        with col2:
            st.markdown("### ⚠️ موارد نیازمند بهبود")
            if result['analysis']['weaknesses']:
                for i, weakness in enumerate(result['analysis']['weaknesses'], 1):
                    st.markdown(f"<div class='warning-box'>{i}. {weakness}</div>", unsafe_allow_html=True)
            else:
                st.success("نقطه ضعف خاصی شناسایی نشد!")
        
        st.divider()
        
        # پیشنهادات
        st.subheader("پیشنهادات بهبود")
        
        if result['recommendations']['general']:
            st.markdown("**توصیه‌های کلی:**")
            for i, rec in enumerate(result['recommendations']['general'], 1):
                st.markdown(f"{i}. {rec}")
        
        if result['recommendations'].get('specific'):
            st.markdown("**توصیه‌های تخصصی:**")
            specific = result['recommendations']['specific']
            if isinstance(specific, dict):
                for criterion, recs in specific.items():
                    if isinstance(recs, list):
                        for rec in recs:
                            st.markdown(f"• {rec}")
                    else:
                        st.markdown(f"• {recs}")
            elif isinstance(specific, list):
                for rec in specific:
                    st.markdown(f"• {rec}")
        
        st.divider()
        
        # هشدارها
        if result.get('warnings'):
            st.subheader("هشدارهای مهم")
            for warning in result['warnings']:
                box_class = f"{warning['severity']}-box"
                st.markdown(
                    f"<div class='{box_class}'><strong>{warning['type']}</strong>: {warning['message']}</div>",
                    unsafe_allow_html=True
                )
        
        st.divider()
        
        # دانلود گزارش
        st.subheader("دانلود گزارش رسمی")
        
        report_json = json.dumps(result, ensure_ascii=False, indent=2)
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 دانلود گزارش JSON",
                data=report_json,
                file_name=f"evaluation_report_{result.get('report_id', 'unknown')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # نمایش خلاصه
            with st.expander("📄 مشاهده خلاصه متنی"):
                st.write(result.get('summary', 'خلاصه در دسترس نیست.'))

# Tab 3: راهنما
with tab3:
    st.header("راهنمای استفاده از سیستم")
    
    st.markdown("""
    ## 📋 دستورالعمل استفاده
    
    ### مرحله 1: ارسال پروپوزال
    1. به تب **"ارسال پروپوزال"** بروید
    2. فایل پروپوزال خود را (PDF یا DOCX) انتخاب کنید
    3. تنظیمات ارزیابی را در سایدبار تنظیم کنید
    4. روی دکمه **"شروع فرآیند ارزیابی"** کلیک کنید
    
    ### مرحله 2: مشاهده نتایج
    1. پس از اتمام ارزیابی، به تب **"نتایج ارزیابی"** بروید
    2. گزارش کامل را مشاهده کنید
    3. می‌توانید گزارش را به صورت JSON دانلود کنید
    
    ## 🎯 معیارهای ارزیابی
    
    سیستم پروپوزال‌ها را بر اساس معیارهای استاندارد زیر ارزیابی می‌کند:
    
    | معیار | وزن | توضیح |
    |-------|------|-------|
    | **نگارش و ساختار** | 45% | املا، گرامر، خوانایی و ساختار استاندارد |
    | **محتوای علمی** | 35% | کیفیت علمی، انسجام و روش‌شناسی |
    | **منابع و ارجاعات** | 15% | کمیت، کیفیت، تنوع و به‌روز بودن منابع |
    | **اصالت و نوآوری** | 5% | عدم تقلب و میزان نوآوری |
    
    ## ⚙️ تنظیمات پیشرفته
    
    ### استفاده از تحلیلگر هوشمند
    - **فعال**: تحلیل عمیق محتوا با استفاده از مدل‌های زبانی بزرگ
    - **غیرفعال**: ارزیابی سریع‌تر بدون تحلیل عمیق
    
    ### نوع گزارش
    - **گزارش جامع**: تمام جزئیات و تحلیل‌ها
    - **گزارش خلاصه**: فقط نتایج اصلی
    
    ## 📝 محدودیت‌ها و نکات فنی
    
    - **حداکثر حجم فایل**: 50 مگابایت
    - **فرمت‌های پشتیبانی شده**: PDF، DOCX، DOC
    - **زبان فایل**: فارسی
    - **زمان ارزیابی**: معمولاً 2-5 دقیقه
    
    ## 🔧 عیب‌یابی مشکلات رایج
    
    ### خطا در اتصال به سیستم
    - مطمئن شوید سرور API در حال اجرا است
    - آدرس API را در سایدبار بررسی کنید (پیش‌فرض: http://localhost:8000)
    
    ### خطا در آپلود فایل
    - حجم فایل باید کمتر از 50 مگابایت باشد
    - فرمت فایل باید PDF یا DOCX باشد
    - فایل نباید رمزگذاری شده باشد
    
    ### زمان‌بر بودن ارزیابی
    - این فرآیند طبیعی است، صبور باشید
    - فایل‌های بزرگتر زمان بیشتری نیاز دارند
    - استفاده از تحلیلگر هوشمند زمان را افزایش می‌دهد
    
    ## � پشتیبانی فنی
    
    در صورت بروز مشکلات فنی:
    1. وضعیت سرور را با کلیک روی "بررسی سلامت سیستم" بررسی کنید
    2. لاگ‌های خطا را مطالعه کنید
    3. از حجم و فرمت فایل اطمینان حاصل کنید
    
    ---
    
    **سیستم ارزیابی هوشمند پروپوزال‌های فارسی - نسخه 1.0.0**  
    **توسعه‌دهنده: تیم فنی پروژه**
    """)
    
    st.divider()
    
    st.subheader("درباره سیستم")
    st.markdown("""
    این سیستم یک نرم‌افزار هوشمند برای ارزیابی خودکار پروپوزال‌های تحقیقاتی فارسی است.
    سیستم با استفاده از تکنیک‌های پیشرفته پردازش زبان طبیعی و مدل‌های زبانی بزرگ،
    ارزیابی‌های دقیق و استانداردی را ارائه می‌دهد.
    
    **ویژگی‌های اصلی:**
    - ارزیابی کاملاً آفلاین و امن
    - تحلیل جامع و چندبعدی
    - گزارش‌های استاندارد و قابل استناد
    - سرعت و دقت بالا
    """)

# Footer
st.markdown(
    '<div class="app-footer">سیستم ارزیابی هوشمند پروپوزال‌های فارسی &nbsp;|&nbsp; نسخه ۱.۰.۰ &nbsp;|&nbsp; رایا هوش فانوس</div>',
    unsafe_allow_html=True
)

