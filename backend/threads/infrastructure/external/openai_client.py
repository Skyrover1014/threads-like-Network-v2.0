from openai import OpenAI
from serpapi import GoogleSearch
from django.conf import settings
from typing import Union

client = OpenAI(
    api_key = settings.OPENAI_API_KEY
)

class OpenAIClient:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.serpapi_key = settings.SERPAPI_API_KEY

    def search_web_v01(self, query: str):

        priority_sites = [
            "site:tfc-taiwan.org.tw",  # ✅ 正式官網
            "site:fact-checker.tw",
            "site:mygopen.com"
        ]
                

        search = GoogleSearch({
            "q": query,
            "api_key": self.serpapi_key,
            "num": 5,
            "hl": "zh-tw",  # 使用繁體中文地區
            "gl": "tw",     # 鎖定台灣地區
            "safe": "active"  # 過濾低可信度或色情資訊
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
    
    def search_web(self, query: str):
        priority_sites = [
            "site:tfc-taiwan.org.tw",  # ✅ TFC 優先
            "site:cna.com.tw",
            "site:twreporter.org"
        ]
        results = []

        # 第一階段：只查可信來源
        for site in priority_sites:
            resp = GoogleSearch({
                "q": f"{query} {site}",
                "api_key": self.serpapi_key,
                "num": 5,
                "hl": "zh-tw",
                "gl": "tw",
                "safe": "active"
            }).get_dict()
            for r in resp.get("organic_results", []):
                link = r.get("link", "").split("\n")[0].strip()
                results.append({
                    "idx": len(results) + 1,
                    "title": r.get("title", "").strip(),
                    "link": link,
                    "snippet": r.get("snippet", "").strip(),
                    "is_tfc": "tfc-taiwan.org.tw" in link
                })
            if len(results) >= 5:
                break

        # 如果第一階段結果不足，才補一般來源
        if len(results) < 5:
            resp = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": 5 - len(results),
                "hl": "zh-tw",
                "gl": "tw",
                "safe": "active"
            }).get_dict()
            for r in resp.get("organic_results", []):
                link = r.get("link", "").split("\n")[0].strip()
                results.append({
                    "idx": len(results) + 1,
                    "title": r.get("title", "").strip(),
                    "link": link,
                    "snippet": r.get("snippet", "").strip(),
                    "is_tfc": False
                })

        return results[:5]
    
    def ask(self, prompt: str) -> str:
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位幫助使用者解答問題的助理，你的目標是根據使用者詢問的事實主題，設計一個好的 Google Search prompt。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def fact_check(self, prompt_or_dict: Union[str, dict]) -> str:
        if isinstance(prompt_or_dict, dict):
            prompt = prompt_or_dict.get("prompt") or ""
            content = prompt_or_dict.get("content")
            query = f"{content}\n{prompt}".strip()
        else:
            content = prompt_or_dict
            prompt = ""
            query = content

        results = self.search_web(query)
 
        # search_text = "\n".join(
        #     f"[{r['idx']}] {r['title']}: {r['snippet']} ({r['link']})"
        #     for r in results
        # )
        # print(search_text)

        # 製作搜尋結果文字（標記 TFC 來源）
        search_text = "\n".join(
            f"{'[TFC]' if r['is_tfc'] else ''}[{r['idx']}] {r['title']}: {r['snippet']} ({r['link']})"
            for r in results
        )
        print(search_text)

        system_msg = "你是一位會根據提供來源以 Markdown 格式回答的查核助理。"
        user_msg = (
            f"{system_msg}\n\n"
            f"以下是搜尋結果（最多 5 筆），請依據內容查核文章真假並提供證據：\n{search_text}\n\n"
            f"使用者提供的原始貼文如下：\n{content}\n\n"
        )

        if prompt:
            user_msg += f"使用者補充的查核問題是：\n{prompt}\n\n"

        user_msg += (
            "請依照以下格式回答：\n"
            "1. 直接說明文章是否正確、有哪些誤導或資訊不足。\n"
            "2. 每個關鍵敘述後標註腳註編號 [^n]。\n"
            "3. 回答用 markdown code block 包起來（```markdown ... ```）。\n"
            "4. 在底部列出所有腳註來源，需要在標注用的index[^n]前面 **使用換行符號**連結後面 **必須空兩格**，不能直接黏著換行、[^n] 或 ```。\n"
                "範例格式：\n[^1]:https://example.com/  \n（注意：連結末端必須有空格）"
        )


        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
        )
        
        return resp.choices[0].message.content