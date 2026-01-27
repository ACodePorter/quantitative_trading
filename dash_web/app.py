import dash
from dash import Dash, html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

from loguru import logger
from utils.set_log import set_log
set_log('dash_web.log')

# 内置主题
THEMES = {
    "Bootstrap": dbc.themes.BOOTSTRAP,
    "Cerulean": dbc.themes.CERULEAN,
    "Cyborg": dbc.themes.CYBORG,
    "Darkly": dbc.themes.DARKLY,
    "Flatly": dbc.themes.FLATLY,
    "Journal": dbc.themes.JOURNAL,
    "Litera": dbc.themes.LITERA,
    "Lumen": dbc.themes.LUMEN,
    "Lux": dbc.themes.LUX,
    "Minty": dbc.themes.MINTY,
    "Pulse": dbc.themes.PULSE,
    "Sandstone": dbc.themes.SANDSTONE,
    "Simplex": dbc.themes.SIMPLEX,
    "Slate": dbc.themes.SLATE,
    "Solar": dbc.themes.SOLAR,
    "Spacelab": dbc.themes.SPACELAB,
    "Superhero": dbc.themes.SUPERHERO,
    "United": dbc.themes.UNITED,
    "Yeti": dbc.themes.YETI,
}

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

# 硬编码的自定义导航顺序
CUSTOM_ORDER = [
    'Home', 
    'Period', 
    'Allocation', 
    'Index', 
    'Metals',
    "Industry",   # 行业
    'Company', 
    'Bond', 
    'Reits', 
    'Virtual',
]

# 简单按自定义顺序获取页面
ordered_pages = []

real_page_name = [page['name'] for page in dash.page_registry.values()]
logger.debug(f'real_page_name: {real_page_name}')

# breakpoint()
for page_name in CUSTOM_ORDER:
    for page in dash.page_registry.values():
        # breakpoint()
        if page['name'] == page_name:
            ordered_pages.append(page)
            break
    else:
        logger.error(f'nav page {page_name} not found')
            # breakpoint()

# 使用排序后的页面或默认顺序
nav_pages = ordered_pages if ordered_pages else list(dash.page_registry.values())
# breakpoint()
app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink(page['name'], 
                      href=page["relative_path"]))
            for page in nav_pages
        ] + [
            dbc.NavItem(
                dcc.Dropdown(
                    id='theme-selector',
                    options=[{"label": k, "value": v} for k, v in THEMES.items()],
                    value=dbc.themes.BOOTSTRAP,
                    clearable=False,
                    style={'width': '120px', 'margin-left': '20px'}
                )
            )
        ],
        brand="Quantitative Trading",
        brand_href="/",
        color="primary",
        dark=True,
        fluid=True
    ),
    # 动态样式表
    html.Link(id="theme-link", rel="stylesheet"),
    dash.page_container
])

# 主题切换回调（记录选择的主题，需要手动修改配置后重启应用）
@callback(
    Output('theme-link', 'href'),
    Input('theme-selector', 'value')
)
def update_theme_store(selected_theme):
    logger.info(f"主题已切换至: {selected_theme}")
    return selected_theme


if __name__ == '__main__':
    logger.info("start dash")
    logger.info("可用主题: " + ", ".join(THEMES.keys()))
    app.run(host='0.0.0.0', port=8050, debug=True)
