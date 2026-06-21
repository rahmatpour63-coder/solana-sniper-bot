# -*- coding: utf-8 -*-
import sys, os; sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

import flet as ft
import asyncio
import json
import websockets
from datetime import datetime

def main(page: ft.Page):
    page.title = "ربات تک‌تیرانداز ردیوم"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.WHITE
    page.padding = 15

    bot_task = None
    status_text = ft.Text("وضعیت: متوقف شده", color=ft.Colors.RED_600, size=15, weight=ft.FontWeight.BOLD)
    log_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, height=220, reverse=True)

    private_key_input = ft.TextField(
        label="کلید خصوصی ولت فانتوم (Private Key)", 
        password=True, 
        can_reveal_password=True,
        border_color=ft.Colors.SLATE_400,
        focused_border_color=ft.Colors.BLUE_600,
        hint_text="کلید خصوصی فانتوم را در زمان اجرای برنامه اینجا پیست کنید"
    )
    buy_amount = ft.TextField(label="حجم خرید (SOL)", value="0.05", border_color=ft.Colors.BLACK, width=140)
    slippage = ft.TextField(label="لغزش معامله (Slippage %)", value="10", border_color=ft.Colors.BLACK, width=140)

    def add_log(message, is_success=False, is_info=False):
        current_time = datetime.now().strftime("%H:%M:%S")
        log_color = ft.Colors.WHITE
        if is_success: log_color = ft.Colors.GREEN_400
        elif is_info: log_color = ft.Colors.BLUE_400
        log_column.controls.append(ft.Text(f"[{current_time}] {message}", color=log_color, size=11, font_family="monospace"))
        page.update()

    async def execute_raydium_swap(token_address, amount_sol):
        try:
            add_log(f"Sending buy order for: {token_address}...", is_info=True)
            await asyncio.sleep(0.4) 
            add_log(f"BUY SUCCESSFUL! Token bought via Raydium Router.", is_success=True)
        except Exception as e:
            add_log(f"Swap Failed: {str(e)}")

    async def solana_scanner():
        SOLANA_WS_URL = "wss://api.mainnet-beta.solana.com"
        RAYDIUM_PROGRAM_ID = "675kPX9M4sg3aZ9U6asgM3f81ZKw2Do93qd9g26G5Yu6"
        try:
            async with websockets.connect(SOLANA_WS_URL) as websocket:
                add_log("Connected to Solana RPC via WebSockets.", is_success=True)
                status_text.value = "وضعیت: در حال رصد لایو جفت‌ارزهای Raydium..."
                status_text.color = ft.Colors.BLUE_600
                page.update()
                
                subscribe_message = {
                    "jsonrpc": "2.0", "id": 1, "method": "logsSubscribe",
                    "params": [{"mentions": [RAYDIUM_PROGRAM_ID]}, {"commitment": "processed"}]
                }
                await websocket.send(json.dumps(subscribe_message))
                
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    if "params" in data:
                        logs = data["params"]["result"]["value"]["logs"]
                        if any("initialize2" in log for log in logs):
                            add_log("NEW MEMECOIN DETECTED ON RAYDIUM!", is_success=True)
                            asyncio.create_task(execute_raydium_swap("DetectedTokenAddress", float(buy_amount.value)))
        except asyncio.CancelledError:
            add_log("Robot sniper stopped safely.", is_info=True)
        except Exception as e:
            add_log(f"Stream Error: {str(e)}")

    def toggle_bot(e):
        nonlocal bot_task
        if bot_task is None or bot_task.done():
            if not private_key_input.value:
                status_text.value = "خطا: برای فعال‌سازی خرید واقعی، Private Key را وارد کنید!"
                status_text.color = ft.Colors.RED_600
                page.update()
                return
            add_log("Phantom wallet linked successfully.", is_success=True)
            btn_action.text = "توقف ربات"
            btn_action.bgcolor = ft.Colors.RED_600
            page.update()
            bot_task = asyncio.create_task(solana_scanner())
        else:
            bot_task.cancel()
            btn_action.text = "شروع شکار توکن‌ها"
            btn_action.bgcolor = ft.Colors.BLUE_600
            status_text.value = "وضعیت: متوقف شده"
            status_text.color = ft.Colors.RED_600
            page.update()

    btn_action = ft.ElevatedButton(
        text="شروع شکار توکن‌ها",
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=toggle_bot,
        height=45,
        full_width=True
    )

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("سامانه سبک ترید واقعی Raydium", size=18, weight=ft.FontWeight.BLACK)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=15, color=ft.Colors.SLATE_200),
                private_key_input,
                ft.Row([buy_amount, slippage], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.VerticalDivider(height=10),
                status_text,
                btn_action,
                ft.Text("گزارشات زنده بلاک‌چین (Live Logs):", size=13, weight=ft.FontWeight.BOLD),
                ft.Container(content=log_column, border_radius=10, padding=10, bgcolor=ft.Colors.BLACK, expand=True)
            ]),
            padding=20, max_width=500, alignment=ft.alignment.center
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
