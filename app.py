from pathlib import Path
import io
import re
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

st.set_page_config(page_title="Energy Dashboard", layout="wide")

language = st.sidebar.selectbox(
    "Language / اللغة",
    ["العربية", "English"]
    
)

if language == "العربية":
    TEXT = {
        "title": "لوحة توازن الطاقة",
        "subtitle": "لوحة تحليل الطاقة للوحدات الفيزيائية والتيراجول",
        "data_source": "اختيار مصدر البيانات",
        "physical": "الوحدات الفيزيائية",
        "terajoule": "التيراجول",
        "filters": "الفلاتر",
        "from_year": "من سنة",
        "to_year": "إلى سنة",
        "select_flows": "اختر التدفقات",
        "energy_type": "اختر نوع الطاقة للتحليل",
        "top_n": "عدد العناصر في الرسومات",
        "sort_by": "ترتيب الجدول حسب",
        "sort_order": "نوع الترتيب",
        "ascending": "تصاعدي",
        "descending": "تنازلي",
        "rows": "عدد الصفوف",
        "dependency": "معدل الاعتمادية",
        "not_available": "غير متاح",
        "table": "الجدول",
        "bar": "الرسم العمودي",
        "pie": "الرسم الدائري",
        "linear": "الانحدار الخطي",
        "multi": "الانحدار الخطي المتعدد",
        "dependency_tab": "الاعتمادية",
        "missing_file": "الملف غير موجود داخل المشروع",
        "read_error": "خطأ في قراءة الملف",
        "empty": "لا توجد بيانات حسب الفلاتر المختارة.",
        "table_after_filter": "الجدول بعد الفلترة",
        "select_columns": "اختر الأعمدة الظاهرة",
        "download_excel": "تحميل الجدول Excel",
        "year_error": "اكتب السنوات بالأرقام الإنجليزية فقط، مثال: 2010",
        "between_years": "السنوات يجب أن تكون بين",
        "range_error": "سنة البداية يجب أن تكون أقل من أو تساوي سنة النهاية.",
        "bar_title": "إجمالي القيم حسب نوع الطاقة",
        "energy_type_axis": "نوع الطاقة",
        "value_axis": "القيمة",
        "pie_title": "توزيع الطاقة في سنة",
        "no_pie": "لا توجد بيانات كافية لرسم الرسم الدائري.",
        "linear_title": "الانحدار الخطي وتنبؤ خمس سنوات",
        "no_linear": "لا توجد بيانات كافية لعمل الانحدار الخطي.",
        "next_forecast": "تنبؤ الخمس سنوات القادمة",
        "multi_title": "الانحدار الخطي المتعدد حسب التدفقات",
        "no_multi": "لا توجد بيانات كافية لعمل الانحدار الخطي المتعدد.",
        "dependency_title": "معدل الاعتمادية على الطاقة",
        "debug": "فحص البيانات",
        "used_file": "الملف المستخدم:",
        "years_found": "السنوات الموجودة:",
        "flows_found": "التدفقات الموجودة:",
        "all": "الكل",
        "year_axis": "السنة",
        "actual": "القيمة الفعلية",
        "predicted": "القيمة المتوقعة",
        "forecast": "التنبؤ",
        "imports": "الواردات",
        "exports": "الصادرات",
        "net_imports": "صافي الواردات",
        "total_supply": "إجمالي إمدادات الطاقة",
        "dependency_components": "مكونات الاعتمادية على الطاقة"
    }
else:
    TEXT = {
        "title": "Energy Balance Dashboard",
        "subtitle": "Dashboard for Physical Units and Terajoule Energy Balance",
        "data_source": "Select Data Source",
        "physical": "Physical Units",
        "terajoule": "Terajoule",
        "filters": "Filters",
        "from_year": "From Year",
        "to_year": "To Year",
        "select_flows": "Select flows",
        "energy_type": "Select energy type for analysis",
        "top_n": "Number of items in charts",
        "sort_by": "Sort table by",
        "sort_order": "Sort order",
        "ascending": "Ascending",
        "descending": "Descending",
        "rows": "Rows",
        "dependency": "Energy Dependency Rate",
        "not_available": "Not Available",
        "table": "Table",
        "bar": "Bar Chart",
        "pie": "Pie Chart",
        "linear": "Linear Regression",
        "multi": "Multi Linear Regression",
        "dependency_tab": "Dependency",
        "missing_file": "File not found in project",
        "read_error": "Error reading file",
        "empty": "No data found based on selected filters.",
        "table_after_filter": "Filtered Table",
        "select_columns": "Select visible columns",
        "download_excel": "Download Excel Table",
        "year_error": "Please enter years using English numbers only, example: 2010",
        "between_years": "Years must be between",
        "range_error": "Start year must be less than or equal to end year.",
        "bar_title": "Total values by energy type",
        "energy_type_axis": "Energy Type",
        "value_axis": "Value",
        "pie_title": "Energy distribution in year",
        "no_pie": "Not enough data to draw Pie Chart.",
        "linear_title": "Linear Regression + 5 Years Forecast",
        "no_linear": "Not enough data to perform Linear Regression.",
        "next_forecast": "Next Five Years Forecast",
        "multi_title": "Multi Linear Regression by flows",
        "no_multi": "Not enough data to perform Multi Linear Regression.",
        "dependency_title": "Energy Dependency Rate",
        "debug": "Data Check",
        "used_file": "Used file:",
        "years_found": "Available years:",
        "flows_found": "Available flows:",
        "all": "All",
        "year_axis": "Year",
        "actual": "Actual",
        "predicted": "Predicted",
        "forecast": "Forecast",
        "imports": "Imports",
        "exports": "Exports",
        "net_imports": "Net Imports",
        "total_supply": "Total Energy Supply",
        "dependency_components": "Energy Dependency Components"
    }

ENERGY_ARABIC = {
    "Solar Energy": "الطاقة الشمسية",
    "Electricity": "الكهرباء",
    "Gasoline": "البنزين",
    "Kerosene": "الكاز",
    "Diesel": "السولار",
    "Bitumen": "البيتومين",
    "Oils and Lubricants": "الزيوت والشحوم",
    "LPG": "غاز البترول المسيل",
    "Olive Cake": "الجفت",
    "Wood and Coal": "الحطب والفحم",
    "Fuel Oil": "زيت الوقود"
}

COLUMN_ARABIC = {
    "year": "السنة",
    "flows": "التدفق",
    **ENERGY_ARABIC
}

FLOW_ARABIC = {
    "primary production": "الإنتاج الأولي",
    "imports": "الواردات",
    "exports": "الصادرات",
    "bunkers": "وقود السفن والطائرات",
    "stock change": "تغير المخزون",
    "total energy requirements": "إجمالي متطلبات الطاقة",
    "total energy supply": "إجمالي إمدادات الطاقة",
    "energy converted": "الطاقة المحولة",
    "electricity generation": "توليد الكهرباء",
    "heat production": "إنتاج الحرارة",
    "consumption for non-energy purposes": "الاستهلاك لأغراض غير طاقية",
    "losses in transport and distribution": "فاقد النقل والتوزيع",
    "statistical differences": "الفروقات الإحصائية",
    "final consumption": "الاستهلاك النهائي",
    "final energy consumption": "الاستهلاك النهائي للطاقة",
    "industry and construction": "الصناعة والإنشاءات",
    "mining": "التعدين",
    "manufacturing": "الصناعة التحويلية",
    "electricity and water supply": "إمدادات الكهرباء والمياه",
    "construction": "الإنشاءات",
    "transport": "النقل",
    "road": "الطرق",
    "household and other sectors": "القطاع المنزلي والقطاعات الأخرى",
    "households": "المنازل",
    "commerce & public services": "التجارة والخدمات العامة",
    "commerce and public services": "التجارة والخدمات العامة",
    "agriculture": "الزراعة",
    "non energy use": "استخدامات غير طاقية",
    "transformation": "التحويل",
    "electricity plants": "محطات الكهرباء",
    "losses": "الفاقد",
    "by industry": "حسب الصناعة",
    "by transport": "حسب النقل",
    "by household and other sectors": "القطاع المنزلي والقطاعات الأخرى"
}

COLOR_PALETTE = [
    "#1F4E79", "#2E86DE", "#27AE60", "#F39C12",
    "#8E44AD", "#E74C3C", "#16A085", "#34495E"
]

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #F8FAFC 0%, #EEF2FF 100%);
}

.title-box {
    background: linear-gradient(135deg, #1E3A8A, #2563EB, #38BDF8);
    padding: 28px;
    border-radius: 22px;
    color: white;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(37, 99, 235, 0.25);
}

.title-box h1 {
    font-size: 38px;
    font-weight: 800;
    margin: 0;
}

.title-box p {
    font-size: 17px;
    opacity: 0.95;
    margin-top: 8px;
}

.card {
    background: rgba(255, 255, 255, 0.96);
    padding: 22px;
    border-radius: 20px;
    border: 1px solid #DBEAFE;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    margin-bottom: 18px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #DBEAFE;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.07);
}

[data-testid="stMetricLabel"] {
    color: #475569;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #1E3A8A;
    font-weight: 800;
}

section[data-testid="stSidebar"] {
    background: #F8FAFC;
    border-right: 1px solid #E2E8F0;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: white;
    border-radius: 14px;
    padding: 10px 18px;
    border: 1px solid #DBEAFE;
    color: #1E3A8A;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #2563EB, #38BDF8);
    color: white;
}

input[type="text"], input[type="number"] {
    direction: ltr;
    unicode-bidi: plaintext;
}
</style>
""", unsafe_allow_html=True)


def clean_text(x):
    return str(x).replace("\n", " ").strip()


def convert_value_to_number(value):
    if pd.isna(value):
        return 0

    text = str(value).strip()

    if text in ["-", ".", "..", "", "nan", "NaN"]:
        return 0

    if text.endswith("-"):
        text = "-" + text[:-1]

    return pd.to_numeric(text, errors="coerce")


def translate_flow_to_arabic(value):
    text = str(value)
    clean_value = re.sub(r"^\s*\d+(\.\d+)*\.?\s*", "", text).strip()

    for english, arabic in FLOW_ARABIC.items():
        if english in clean_value.lower():
            return arabic

    return text


def translate_table_to_arabic(dataframe):
    translated_df = dataframe.copy()

    if "flows" in translated_df.columns:
        translated_df["flows"] = translated_df["flows"].apply(translate_flow_to_arabic)

    translated_df = translated_df.rename(columns=COLUMN_ARABIC)
    return translated_df


def translate_energy_name(name):
    if language == "العربية":
        return ENERGY_ARABIC.get(name, name)
    return name


def translate_energy_dataframe(dataframe):
    translated_df = dataframe.copy()

    if language == "العربية" and "Energy Type" in translated_df.columns:
        translated_df["Energy Type"] = translated_df["Energy Type"].replace(ENERGY_ARABIC)

    return translated_df


def read_energy_file(file_source):
    raw = pd.read_excel(file_source, sheet_name=0, header=None)

    header_row = None
    for i in range(min(30, len(raw))):
        values = [clean_text(v).lower() for v in raw.iloc[i].tolist()]
        if "year" in values:
            header_row = i
            break

    if header_row is None:
        raise ValueError("Year column was not found.")

    headers = [clean_text(v) for v in raw.iloc[header_row].tolist()]
    if headers[0] == "" or headers[0].lower() == "nan":
        headers[0] = "flows"

    df = raw.iloc[header_row + 1:].copy()
    df.columns = headers

    df = df.loc[:, [str(c).strip() != "" and str(c).lower() != "nan" for c in df.columns]]
    df.columns = [clean_text(c) for c in df.columns]

    year_col = None
    for col in df.columns:
        if clean_text(col).lower() == "year":
            year_col = col
            break

    df = df.rename(columns={year_col: "year"})

    if "flows" not in df.columns:
        df = df.rename(columns={df.columns[0]: "flows"})

    df = df.dropna(how="all").copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["year"]).copy()
    df["year"] = df["year"].astype(int)

    df["flows"] = df["flows"].astype(str).str.strip()
    df = df[df["flows"] != ""]
    df = df[df["flows"].str.lower() != "nan"]

    numeric_cols = [c for c in df.columns if c not in ["flows", "year"]]

    for col in numeric_cols:
        df[col] = df[col].apply(convert_value_to_number).fillna(0)

    if not numeric_cols:
        raise ValueError("No numeric columns found.")

    return df, numeric_cols


@st.cache_data
def load_data(local_path):
    return read_energy_file(local_path)


def to_excel_bytes(dataframe):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Filtered Data")
    output.seek(0)
    return output.getvalue()
def build_regression(data, target_col):
    yearly = data.groupby("year", as_index=False)[target_col].sum().sort_values("year")

    if len(yearly) < 2:
        return None, None, None

    X = yearly[["year"]]
    y = yearly[target_col]

    model = LinearRegression()
    model.fit(X, y)

    yearly["Actual"] = y
    yearly["Predicted"] = model.predict(X)

    r2 = r2_score(y, yearly["Predicted"])

    last_year = int(yearly["year"].max())
    future_years = list(range(last_year + 1, last_year + 6))

    future_forecast = pd.DataFrame({"year": future_years})
    future_forecast["Forecast"] = model.predict(future_forecast[["year"]])

    return yearly, r2, future_forecast


def build_multi_regression(data, target_col):
    results = []

    for flow in data["flows"].unique():
        flow_data = data[data["flows"] == flow]
        yearly = flow_data.groupby("year", as_index=False)[target_col].sum().sort_values("year")

        if len(yearly) < 2:
            continue

        X = yearly[["year"]]
        y = yearly[target_col]

        model = LinearRegression()
        model.fit(X, y)

        yearly["Actual"] = y
        yearly["Predicted"] = model.predict(X)
        yearly["flows"] = flow

        results.append(yearly)

    if not results:
        return None

    return pd.concat(results, ignore_index=True)


def calculate_energy_dependency(data, energy_cols):
    imports_keywords = ["imports", "import"]
    exports_keywords = ["exports", "export"]
    supply_keywords = ["total energy supply", "total energy requirements"]

    imports_value = 0
    exports_value = 0
    supply_value = 0

    for flow in data["flows"].unique():
        flow_text = str(flow).lower().strip()
        flow_rows = data[data["flows"] == flow]
        total_value = flow_rows[energy_cols].sum().sum()

        if any(keyword in flow_text for keyword in imports_keywords):
            imports_value += total_value

        if any(keyword in flow_text for keyword in exports_keywords):
            exports_value += total_value

        if any(keyword in flow_text for keyword in supply_keywords):
            supply_value += total_value

    net_imports = imports_value + exports_value

    if supply_value == 0:
        return None, imports_value, exports_value, net_imports, supply_value

    dependency_rate = (net_imports / supply_value) * 100

    return dependency_rate, imports_value, exports_value, net_imports, supply_value


st.markdown(f"""
<div class="title-box">
    <h1>{TEXT["title"]}</h1>
    <p>{TEXT["subtitle"]}</p>
</div>
""", unsafe_allow_html=True)


BASE_DIR = Path(__file__).resolve().parent

PHYSICAL_FILE = BASE_DIR / "physical.xlsx"
TERAJOULE_FILE = BASE_DIR / "terajoul.xlsx"

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(TEXT["data_source"])

unit_type = st.radio(
    TEXT["data_source"],
    [TEXT["physical"], TEXT["terajoule"]],
    horizontal=True
)

if unit_type == TEXT["physical"]:
    file_path = PHYSICAL_FILE
    used_file_name = "physical.xlsx"
else:
    file_path = TERAJOULE_FILE
    used_file_name = "terajoul.xlsx"

try:
    if not file_path.exists():
        st.error(f"{TEXT['missing_file']}: {used_file_name}")
        st.stop()

    df, energy_cols = load_data(str(file_path))

except Exception as e:
    st.error(f"{TEXT['read_error']}: {e}")
    st.stop()

st.markdown('</div>', unsafe_allow_html=True)


years = sorted(df["year"].unique().tolist())
flows = sorted(df["flows"].dropna().unique().tolist())

with st.sidebar:
    st.header(TEXT["filters"])

    c1, c2 = st.columns(2)

    min_year = int(min(years))
    max_year = int(max(years))

    with c1:
        start_year_text = st.text_input(TEXT["from_year"], value=str(min_year))

    with c2:
        end_year_text = st.text_input(TEXT["to_year"], value=str(max_year))

    try:
        start_year = int(start_year_text.strip())
        end_year = int(end_year_text.strip())
    except ValueError:
        st.error(TEXT["year_error"])
        st.stop()

    if start_year < min_year or end_year > max_year:
        st.error(f"{TEXT['between_years']} {min_year} - {max_year}.")
        st.stop()

    if start_year > end_year:
        st.error(TEXT["range_error"])
        st.stop()

    if language == "العربية":
        translated_flows = [translate_flow_to_arabic(flow) for flow in flows]
        flow_map = dict(zip(translated_flows, flows))

        selected_flows_ar = st.multiselect(
            TEXT["select_flows"],
            options=[TEXT["all"]] + translated_flows,
            default=[TEXT["all"]]
        )

        if TEXT["all"] in selected_flows_ar:
            selected_flows = ["All"]
        else:
            selected_flows = [flow_map[x] for x in selected_flows_ar]
    else:
        selected_flows = st.multiselect(
            TEXT["select_flows"],
            options=[TEXT["all"]] + flows,
            default=[TEXT["all"]]
        )

    if language == "العربية":
        available_energy_ar = [ENERGY_ARABIC.get(col, col) for col in energy_cols]
        energy_map = dict(zip(available_energy_ar, energy_cols))

        selected_energy_ar = st.selectbox(
            TEXT["energy_type"],
            options=available_energy_ar
        )

        selected_energy = energy_map[selected_energy_ar]
    else:
        selected_energy = st.selectbox(
            TEXT["energy_type"],
            options=energy_cols
        )

    top_n = st.slider(
        TEXT["top_n"],
        min_value=3,
        max_value=min(20, len(energy_cols)),
        value=min(8, len(energy_cols))
    )

    sort_options = df.columns.tolist()

    if language == "العربية":
        sort_display_options = [COLUMN_ARABIC.get(col, col) for col in sort_options]
        sort_map = dict(zip(sort_display_options, sort_options))

        sort_table_by_display = st.selectbox(
            TEXT["sort_by"],
            options=sort_display_options,
            index=0
        )

        sort_table_by = sort_map[sort_table_by_display]
    else:
        sort_table_by = st.selectbox(
            TEXT["sort_by"],
            options=sort_options,
            index=0
        )

    sort_order = st.radio(
        TEXT["sort_order"],
        [TEXT["ascending"], TEXT["descending"]],
        horizontal=True
    )


filtered_df = df[
    (df["year"] >= int(start_year)) &
    (df["year"] <= int(end_year))
].copy()

if TEXT["all"] not in selected_flows and "All" not in selected_flows and len(selected_flows) > 0:
    filtered_df = filtered_df[filtered_df["flows"].isin(selected_flows)].copy()

filtered_df = filtered_df.sort_values(
    by=sort_table_by,
    ascending=(sort_order == TEXT["ascending"])
)

if filtered_df.empty:
    st.warning(TEXT["empty"])
    st.stop()


show_dependency = unit_type == TEXT["terajoule"]

dependency_rate = None
imports_value = 0
exports_value = 0
net_imports = 0
supply_value = 0

if show_dependency:
    dependency_rate, imports_value, exports_value, net_imports, supply_value = calculate_energy_dependency(
        filtered_df,
        energy_cols
    )


if show_dependency:
    c1, c2, c3, c4 = st.columns(4)
else:
    c1, c2, c3 = st.columns(3)

c1.metric(TEXT["from_year"], str(int(start_year)))
c2.metric(TEXT["to_year"], str(int(end_year)))
c3.metric(TEXT["rows"], f"{len(filtered_df):,}")

if show_dependency:
    if dependency_rate is not None:
        c4.metric(TEXT["dependency"], f"{dependency_rate:.2f}%")
    else:
        c4.metric(TEXT["dependency"], TEXT["not_available"])


bar_data = filtered_df[energy_cols].sum().reset_index()
bar_data.columns = ["Energy Type", "Value"]
bar_data = bar_data.sort_values("Value", ascending=False).head(top_n)
bar_data = translate_energy_dataframe(bar_data)

latest_year = filtered_df["year"].max()

pie_data = filtered_df[filtered_df["year"] == latest_year][energy_cols].sum().reset_index()
pie_data.columns = ["Energy Type", "Value"]
pie_data = pie_data[pie_data["Value"] > 0].sort_values("Value", ascending=False).head(top_n)
pie_data = translate_energy_dataframe(pie_data)

regression_data, r2, future_forecast = build_regression(filtered_df, selected_energy)
multi_regression_data = build_multi_regression(filtered_df, selected_energy)


tab_names = [
    TEXT["table"],
    TEXT["bar"],
    TEXT["pie"],
    TEXT["linear"],
    TEXT["multi"]
]

if show_dependency:
    tab_names.append(TEXT["dependency_tab"])

tabs = st.tabs(tab_names)

tab1, tab2, tab3, tab4, tab5 = tabs[:5]

if show_dependency:
    tab6 = tabs[5]


with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(TEXT["table_after_filter"])

    default_cols = ["year", "flows"] + energy_cols[:6]
    default_cols = [c for c in default_cols if c in filtered_df.columns]

    if language == "العربية":
        columns_display = [COLUMN_ARABIC.get(col, col) for col in filtered_df.columns.tolist()]
        columns_map = dict(zip(columns_display, filtered_df.columns.tolist()))
        default_display_cols = [COLUMN_ARABIC.get(col, col) for col in default_cols]

        selected_columns_display = st.multiselect(
            TEXT["select_columns"],
            options=columns_display,
            default=default_display_cols
        )

        selected_columns = [columns_map[col] for col in selected_columns_display]
    else:
        selected_columns = st.multiselect(
            TEXT["select_columns"],
            options=filtered_df.columns.tolist(),
            default=default_cols
        )

    if selected_columns:
        table_df = filtered_df[selected_columns]

        if language == "العربية":
            display_table_df = translate_table_to_arabic(table_df)
        else:
            display_table_df = table_df

        st.dataframe(display_table_df, use_container_width=True, height=520)

        st.download_button(
            label=TEXT["download_excel"],
            data=to_excel_bytes(table_df),
            file_name="filtered_energy_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info(TEXT["select_columns"])

    st.markdown('</div>', unsafe_allow_html=True)


with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(TEXT["bar"])

    fig_bar = px.bar(
        bar_data,
        x="Energy Type",
        y="Value",
        text="Value",
        title=TEXT["bar_title"],
        color="Energy Type",
        color_discrete_sequence=COLOR_PALETTE
    )

    fig_bar.update_layout(
        template="plotly_white",
        xaxis_title=TEXT["energy_type_axis"],
        yaxis_title=TEXT["value_axis"],
        dragmode="zoom",
        showlegend=False,
        bargap=0.05,
        bargroupgap=0.01
    )

    fig_bar.update_traces(
        textposition="outside",
        marker_line_width=1.5,
        width=0.8
    )

    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(TEXT["pie"])

    if pie_data.empty:
        st.info(TEXT["no_pie"])
    else:
        fig_pie = px.pie(
            pie_data,
            names="Energy Type",
            values="Value",
            hole=0.4,
            title=f"{TEXT['pie_title']} {latest_year}",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig_pie.update_layout(template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(TEXT["linear_title"])

    if regression_data is None:
        st.info(TEXT["no_linear"])
    else:
        reg_plot = regression_data.copy()
        reg_plot["Forecast"] = None

        future_plot = future_forecast.copy()
        future_plot["Actual"] = None
        future_plot["Predicted"] = None

        combined = pd.concat([reg_plot, future_plot], ignore_index=True)

        if language == "العربية":
            combined = combined.rename(columns={
                "Actual": TEXT["actual"],
                "Predicted": TEXT["predicted"],
                "Forecast": TEXT["forecast"]
            })

            y_columns = [TEXT["actual"], TEXT["predicted"], TEXT["forecast"]]
        else:
            y_columns = ["Actual", "Predicted", "Forecast"]

        fig_reg = px.line(
            combined,
            x="year",
            y=y_columns,
            markers=True,
            title=f"{TEXT['linear_title']} - {translate_energy_name(selected_energy)}",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig_reg.update_layout(
            template="plotly_white",
            xaxis_title=TEXT["year_axis"],
            yaxis_title=TEXT["value_axis"],
            dragmode="zoom"
        )

        st.plotly_chart(fig_reg, use_container_width=True)
        st.metric("R²", f"{r2:.3f}")

        st.subheader(TEXT["next_forecast"])

        if language == "العربية":
            display_forecast = future_forecast.rename(columns={
                "year": TEXT["year_axis"],
                "Forecast": TEXT["forecast"]
            })
        else:
            display_forecast = future_forecast

        st.dataframe(display_forecast, use_container_width=True, height=250)

    st.markdown('</div>', unsafe_allow_html=True)


with tab5:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(TEXT["multi_title"])

    if multi_regression_data is None:
        st.warning(TEXT["no_multi"])
    else:
        long_multi = multi_regression_data.melt(
            id_vars=["year", "flows"],
            value_vars=["Actual", "Predicted"],
            var_name="Type",
            value_name="Value"
        )

        if language == "العربية":
            long_multi["flows"] = long_multi["flows"].apply(translate_flow_to_arabic)
            long_multi["Type"] = long_multi["Type"].replace({
                "Actual": TEXT["actual"],
                "Predicted": TEXT["predicted"]
            })

        long_multi["Line"] = long_multi["flows"] + " - " + long_multi["Type"]

        fig_multi = px.line(
            long_multi,
            x="year",
            y="Value",
            color="Line",
            markers=True,
            title=f"{TEXT['multi_title']} - {translate_energy_name(selected_energy)}",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig_multi.update_layout(
            template="plotly_white",
            xaxis_title=TEXT["year_axis"],
            yaxis_title=TEXT["value_axis"]
        )

        st.plotly_chart(fig_multi, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


if show_dependency:
    with tab6:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader(TEXT["dependency_title"])

        if language == "العربية":
            st.code("معدل الاعتمادية = صافي الواردات / إجمالي إمدادات الطاقة × 100")
            st.code("صافي الواردات = الواردات + الصادرات")
        else:
            st.code("Energy Dependency Rate = Net Imports / Total Energy Supply × 100")
            st.code("Net Imports = Imports + Exports")

        a, b, c, d = st.columns(4)

        a.metric(TEXT["imports"], f"{imports_value:,.2f}")
        b.metric(TEXT["exports"], f"{exports_value:,.2f}")
        c.metric(TEXT["net_imports"], f"{net_imports:,.2f}")
        d.metric(TEXT["total_supply"], f"{supply_value:,.2f}")

        if dependency_rate is not None:
            st.metric(TEXT["dependency"], f"{dependency_rate:.2f}%")
        else:
            st.metric(TEXT["dependency"], TEXT["not_available"])

        dependency_df = pd.DataFrame({
            "Indicator": [
                TEXT["imports"],
                TEXT["exports"],
                TEXT["net_imports"],
                TEXT["total_supply"]
            ],
            "Value": [imports_value, exports_value, net_imports, supply_value]
        })

        fig_dependency = px.bar(
            dependency_df,
            x="Indicator",
            y="Value",
            text="Value",
            title=TEXT["dependency_components"],
            color="Indicator",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig_dependency.update_layout(
            template="plotly_white",
            showlegend=False,
            bargap=0.10,
            xaxis_title="",
            yaxis_title=TEXT["value_axis"]
        )

        fig_dependency.update_traces(
            textposition="outside",
            width=0.7
        )

        st.plotly_chart(fig_dependency, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


with st.expander(TEXT["debug"]):
    st.write(TEXT["used_file"])
    st.write(used_file_name)

    st.write(TEXT["years_found"])
    st.write(years)

    st.write(TEXT["flows_found"])

    if language == "العربية":
        st.write([translate_flow_to_arabic(flow) for flow in flows])
    else:
        st.write(flows)

    preview_df = df.head()

    if language == "العربية":
        preview_df = translate_table_to_arabic(preview_df)

    st.dataframe(preview_df, use_container_width=True)