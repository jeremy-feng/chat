# -*- coding: UTF-8 -*-
import dash
from server import app
import openai
from dash import html, dcc
import feffery_antd_components as fac
import feffery_utils_components as fuc
import feffery_markdown_components as fmc
from dash.dependencies import Input, Output, State

from config import Config

# 本地运行需要开启代理
import sys

if sys.argv[1] == "local":
    import os

    os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
    os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"


# 载入 openai api key
openai.api_key = Config.openai_api_key

server = app.server
app.layout = fac.AntdWatermark(
    html.Div(
        fuc.FefferyDiv(
            [
                fac.AntdParagraph(
                    [
                        fac.AntdText(
                            "在线问答机器人", strong=True, italic=True, style={"fontSize": 22}
                        ),
                        fac.AntdText(
                            "（基于 OpenAI ChatGPT 接口+feffery components）",
                            type="secondary",
                            style={"fontSize": 10},
                        ),
                    ]
                ),
                # 聊天记录容器
                html.Div(
                    [
                        fac.AntdSpace(
                            [
                                fac.AntdAvatar(
                                    mode="icon",
                                    icon="antd-robot",
                                    style={"background": "#1890ff"},
                                ),
                                fuc.FefferyDiv(
                                    fac.AntdParagraph(
                                        ["你好，欢迎使用基于 ChatGPT 服务的在线聊天机器人😋"]
                                    ),
                                    style={
                                        "background": "white",
                                        "borderRadius": 6,
                                        "padding": 15,
                                        "boxShadow": "0 2px 12px 0 rgb(0 0 0 / 10%)",
                                    },
                                ),
                            ],
                            align="start",
                            style={"padding": "10px 15px", "width": "100%"},
                        )
                    ],
                    id="chat-records",
                    style={
                        "height": 600,
                        "overflowY": "auto",
                        "boxShadow": "inset 0px 0px 5px 1px #dee2e6",
                        "marginBottom": 5,
                        "background": "#f8f9fa",
                    },
                ),
                # 聊天输入区
                fac.AntdSpace(
                    [
                        fac.AntdInput(
                            id="new-question-input",
                            mode="text-area",
                            autoSize=False,
                            allowClear=True,
                            placeholder="请输入问题：",
                            size="large",
                        ),
                        fac.AntdButton(
                            "提交",
                            id="send-new-question",
                            type="primary",
                            block=True,
                            autoSpin=True,
                            loadingChildren="思考中",
                            size="large",
                        ),
                    ],
                    direction="vertical",
                    size=2,
                    style={"width": "100%"},
                ),
            ],
            shadow="always-shadow",
            style={
                "width": 800,
                "borderRadius": 12,
                "margin": "0 auto",
                "background": "white",
                "padding": 20,
            },
        ),
        style={"padding": "50px 0", "background": "#f8f9fa", "minHeight": "100vh"},
    ),
)


@app.callback(
    [
        Output("chat-records", "children"),
        Output("new-question-input", "value"),
        Output("send-new-question", "loading"),
    ],
    Input("send-new-question", "nClicks"),
    [State("new-question-input", "value"), State("chat-records", "children")],
    prevent_initial_call=True,
)
def send_new_question(nClicks, question, origin_children):

    if nClicks and question:

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": question}]
        )

        return [
            [
                *origin_children,
                # 渲染当前问题
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode="text", text="我", style={"background": "#1890ff"}
                        ),
                        fuc.FefferyDiv(
                            fac.AntdParagraph([question], copyable=True),
                            style={
                                "background": "white",
                                "borderRadius": 6,
                                "padding": 15,
                                "boxShadow": "0 2px 12px 0 rgb(0 0 0 / 10%)",
                                "maxWidth": 680,
                            },
                        ),
                    ],
                    align="start",
                    style={
                        "padding": "10px 15px",
                        "width": "100%",
                        "flexDirection": "row-reverse",
                    },
                ),
                # 渲染当前问题的回复
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode="icon",
                            icon="antd-robot",
                            style={"background": "#1890ff"},
                        ),
                        fuc.FefferyDiv(
                            fmc.FefferyMarkdown(
                                markdownStr=response["choices"][0]["message"][
                                    "content"
                                ],
                                codeTheme="a11y-dark",
                            ),
                            style={
                                "background": "white",
                                "borderRadius": 6,
                                "padding": 15,
                                "boxShadow": "0 2px 12px 0 rgb(0 0 0 / 10%)",
                                "maxWidth": 680,
                            },
                        ),
                    ],
                    align="start",
                    style={"padding": "10px 15px", "width": "100%"},
                ),
            ],
            None,
            False,
        ]

    return dash.no_update


if __name__ == "__main__":
    app.run_server(debug=False)
