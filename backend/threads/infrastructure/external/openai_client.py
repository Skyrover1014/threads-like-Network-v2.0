from openai import OpenAI
from serpapi import GoogleSearch
from django.conf import settings
import re

client = OpenAI(
    api_key = settings.OPENAI_API_KEY
)

class OpenAIClient:
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
        self.serpapi_key = settings.SERPAPI_API_KEY

    def search_web(self, query: str):
        search = GoogleSearch({
            "q": query,
            "api_key": self.serpapi_key,
            "num": 5
        })
        data = search.get_dict()
        results = []
        for idx, r in enumerate(data.get("organic_results", []), start=1):
            title = r.get("title")
            link = r.get("link", "").strip().split('\n')[0]
            snippet = r.get("snippet", "").strip()
            results.append({
                "idx": idx,
                "title": title,
                "link": link,
                "snippet": snippet
            })
        return results

    def ask_with_web_search(self, prompt: str) -> str:
        results = self.search_web(prompt)
        search_text = "\n".join(
            f"[{r['idx']}] {r['title']}: {r['snippet']} ({r['link']})"
            for r in results
        )
        system_msg = "你是一位會根據提供來源以 Markdown 格式回答的查核助理。"
        user_msg = (
            f"{system_msg}\n\n"
            f"以下是搜尋結果，請依此查核問題：\n{search_text}\n\n"
            f"問題：{prompt}\n\n"
            "請依照以下格式回答：\n"
            "1. 用 Markdown 格式回答，每一句結論或數據後用 [^n] 編號，且從 [^1] 依序連番，不可跳號。\n"
            "2. 回答全文請包在 markdown code block 裡（```markdown … ```），確保原始格式不被前端渲染。\n"
            "3. 底部列出所有腳註來源連結，腳註編號必須與內文一致。\n"
            "4. 來源連結的url尾端，不要直接黏著換行符號或 footnote 標記 `[^n]`，至少要有些空格後再接換行符號，例如：[^1]:https://example.com/   換行符號[^2]:https://example.com/"
        )
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
        )
        return resp.choices[0].message.content
    
    def ask(self, prompt: str) -> str:
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位幫助使用者解答問題的助理。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content