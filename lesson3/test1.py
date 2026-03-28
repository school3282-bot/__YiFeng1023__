"""
title: Example Filter
author: open-webui
author_url: https://github.com/open-webui
funding_url: https://github.com/open-webui
version: 0.1

這是一個 Open WebUI 的 Filter（過濾器）插件範例。
Filter 可以在訊息送出前（inlet）和收到回應後（outlet）進行攔截與處理。
"""

from pydantic import BaseModel, Field
from typing import Optional


class Filter:
    """
    Filter 類別：Open WebUI 的過濾器插件主體。
    包含兩種設定閥（Valves）：
    - Valves：管理員層級的全域設定
    - UserValves：個別使用者的設定
    """

    class Valves(BaseModel):
        """
        管理員全域設定。
        這些設定由管理員在後台配置，對所有使用者生效。
        """
        priority: int = Field(
            default=0, description="Priority level for the filter operations."
            # 過濾器的優先順序，數字越小越優先執行
        )
        max_turns: int = Field(
            default=8, description="Maximum allowable conversation turns for a user."
            # 全域最大對話輪數上限，預設為 8 輪
        )
        pass

    class UserValves(BaseModel):
        """
        使用者個人設定。
        每位使用者可以自行調整，但不能超過管理員設定的上限。
        """
        max_turns: int = Field(
            default=4, description="Maximum allowable conversation turns for a user."
            # 使用者自己的最大對話輪數，預設為 4 輪
        )
        pass

    def __init__(self):
        """
        初始化 Filter 插件。
        建立 Valves 實例，載入預設的全域設定。
        """
        # 若要自訂檔案處理邏輯，可取消下方註解。
        # 啟用後，WebUI 會將檔案相關操作交由此類別的方法處理，
        # 而不使用預設的檔案處理流程。
        # self.file_handler = True

        # 初始化全域設定（Valves），將所有設定集中管理，
        # 避免與 file_handler 等操作旗標混淆。
        self.valves = self.Valves()
        pass

    def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        入口攔截器（前處理器）。
        在使用者的訊息送往 AI 模型之前執行。
        可用於：驗證輸入、修改請求內容、限制使用條件等。

        參數：
            body (dict)：請求主體，包含對話訊息等資訊
            __user__ (dict)：當前使用者資訊，包含角色與個人設定

        回傳：
            dict：處理後的請求主體
        """
        # 印出除錯資訊，方便開發時追蹤執行狀況
        print(f"inlet:{__name__}")
        print(f"inlet:body:{body}")
        print(f"inlet:user:{__user__}")

        # 只對 "user" 和 "admin" 角色進行對話輪數限制
        if __user__.get("role", "admin") in ["user", "admin"]:
            messages = body.get("messages", [])  # 取得目前的對話訊息列表

            # 取使用者設定與全域設定中較小的值，確保不超過管理員上限
            max_turns = min(__user__["valves"].max_turns, self.valves.max_turns)

            # 若對話輪數超過上限，拋出例外阻止繼續對話
            if len(messages) > max_turns:
                raise Exception(
                    f"Conversation turn limit exceeded. Max turns: {max_turns}"
                    # 對話輪數已超過限制，顯示最大允許輪數
                )

        return body  # 回傳（可能已修改的）請求主體

    def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
        """
        出口攔截器（後處理器）。
        在 AI 模型回應之後、顯示給使用者之前執行。
        可用於：分析回應內容、記錄日誌、修改回應等。

        參數：
            body (dict)：回應主體，包含 AI 的回覆內容
            __user__ (dict)：當前使用者資訊

        回傳：
            dict：處理後的回應主體
        """
        # 印出除錯資訊
        print(f"outlet:{__name__}")
        print(f"outlet:body:{body}")
        print(f"outlet:user:{__user__}")

        return body  # 回傳（可能已修改的）回應主體
