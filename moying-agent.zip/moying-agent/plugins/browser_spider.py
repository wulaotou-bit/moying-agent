"""
墨影番茄/起点作家后台爬虫插件
功能：
1. 自动登录（Cookie加密持久化）
2. 自动发布章节
3. 爬取读者评论
4. 爬取数据中心数据
选择器：全部模糊匹配，防平台改版
"""
from plugins.browser_core import BrowserCore
from utils.decorators import auto_retry
from utils.logger import log
from config import Config
import time
import random
from datetime import datetime

class NovelSpider(BrowserCore):
    def __init__(self, platform: str = "fanqie"):
        super().__init__(platform)
        self.platform_urls = {
            "fanqie": "https://writer.m.toutiao.com",
            "qidian": "https://write.qidian.com"
        }
        self.current_url = self.platform_urls.get(platform, "https://writer.m.toutiao.com")

    def _human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """人类行为模拟：随机延迟"""
        delay = random.randint(min_ms, max_ms) / 1000
        time.sleep(delay)

    def _human_scroll(self):
        """人类行为模拟：随机滚动"""
        for _ in range(random.randint(1, 3)):
            self.page.mouse.wheel(0, random.randint(100, 300))
            self._human_delay(200, 500)

    def _check_login_status(self) -> bool:
        """检查登录状态：模糊匹配URL或元素"""
        try:
            self._human_delay(1000, 2000)
            if "writer" in self.page.url or "write" in self.page.url:
                if self.page.query_selector('button:has-text("发布")') or self.page.query_selector('a:has-text("发布")'):
                    return True
            return False
        except:
            return False

    @auto_retry
    def login(self):
        """自动登录：Cookie优先，失败则账号密码登录"""
        log.info(f"【{self.platform}】正在登录...")
        self.init_browser()
        self.page.goto(self.current_url, wait_until="networkidle")
        self._human_delay(1000, 2000)

        # 尝试加载Cookie
        if self.load_cookies():
            self.page.reload(wait_until="networkidle")
            if self._check_login_status():
                log.success(f"【{self.platform}】Cookie免登录成功")
                return

        # Cookie失败，账号密码登录
        log.warning(f"【{self.platform}】Cookie失效，使用账号密码登录")
        account = Config.PLATFORM_ACCOUNTS[self.platform]

        try:
            # 模糊匹配输入框（多个备选）
            username_input = self.page.wait_for_selector(
                'input[type="text"], input[placeholder*="账号"], input[placeholder*="手机"], input[placeholder*="邮箱"]',
                timeout=10000
            )
            username_input.fill(account["user"])
            self._human_delay()

            password_input = self.page.wait_for_selector(
                'input[type="password"], input[placeholder*="密码"]',
                timeout=10000
            )
            password_input.fill(account["pwd"])
            self._human_delay()

            login_button = self.page.wait_for_selector(
                'button:has-text("登录"), button:has-text("登 录"), a:has-text("登录")',
                timeout=10000
            )
            login_button.click()
            log.warning(f"【{self.platform}】请手动完成滑块/验证码验证（15秒内）")
            time.sleep(15)

            if self._check_login_status():
                self.save_cookies()
                log.success(f"【{self.platform}】登录成功，Cookie已加密保存")
            else:
                raise Exception("登录失败，请检查账号密码或手动验证")
        except Exception as e:
            log.error(f"【{self.platform}】登录失败: {e}")
            raise

    @auto_retry
    def publish_chapter(self, title: str, content: str):
        """自动发布章节"""
        log.info(f"【{self.platform}】正在发布章节: {title}")
        try:
            # 多个备选选择器（防平台改版）
            publish_btn = self.page.wait_for_selector(
                'button:has-text("发布新章节"), button:has-text("发布章节"), a:has-text("发布新章节"), div[role="button"]:has-text("发布")',
                timeout=10000
            )
            publish_btn.click()
            self._human_delay(1000, 2000)

            title_input = self.page.wait_for_selector(
                'input[placeholder*="标题"], input[placeholder*="章节标题"]',
                timeout=10000
            )
            title_input.fill(title)
            self._human_delay()

            content_area = self.page.wait_for_selector(
                'div[role="textbox"], textarea[placeholder*="内容"], textarea[placeholder*="正文"]',
                timeout=10000
            )
            content_area.fill(content)
            self._human_delay(1000, 2000)

            submit_btn = self.page.wait_for_selector(
                'button:has-text("立即发布"), button:has-text("发布"), button:has-text("确认发布")',
                timeout=10000
            )
            submit_btn.click()
            self._human_delay(3000, 5000)

            # 检查是否发布成功
            if self.page.query_selector('text=发布成功') or self.page.query_selector('text=已发布'):
                log.success(f"【{self.platform}】章节发布成功！")
            else:
                log.warning(f"【{self.platform}】未检测到发布成功提示，但继续执行")

            # 截图保存发布记录
            screenshot_path = Config.OUTPUT_DIR / f"发布记录_{title}.png"
            self.page.screenshot(path=str(screenshot_path), full_page=True)
            log.info(f"发布记录截图已保存: {screenshot_path}")
        except Exception as e:
            log.error(f"【{self.platform}】章节发布失败: {e}")
            raise

    @auto_retry
    def crawl_comments(self) -> list:
        """爬取读者评论"""
        log.info(f"【{self.platform}】正在爬取读者评论...")
        try:
            comment_btn = self.page.wait_for_selector(
                'button:has-text("评论"), a:has-text("评论"), div:has-text("评论")',
                timeout=10000
            )
            comment_btn.click()
            self._human_delay(1000, 2000)
            self._human_scroll()

            comments = []
            comment_items = self.page.query_selector_all(
                'div[class*="comment"], div[class*="item"]:has(span[class*="name"])'
            )[:20]

            for item in comment_items:
                try:
                    username = item.query_selector('span[class*="name"], span:has-text("@")').inner_text() if item.query_selector('span[class*="name"], span:has-text("@")') else "匿名"
                    content = item.query_selector('div[class*="content"], p').inner_text() if item.query_selector('div[class*="content"], p') else ""
                    time_str = item.query_selector('span[class*="time"], span:has-text("前")').inner_text() if item.query_selector('span[class*="time"], span:has-text("前")') else ""
                    comments.append({
                        "username": username.strip(),
                        "content": content.strip(),
                        "time": time_str.strip()
                    })
                except:
                    continue

            log.success(f"【{self.platform}】爬取评论成功！共{len(comments)}条")
            return comments
        except Exception as e:
            log.error(f"【{self.platform}】爬取评论失败: {e}")
            return []

    @auto_retry
    def crawl_data(self) -> dict:
        """爬取数据中心数据"""
        log.info(f"【{self.platform}】正在爬取数据中心数据...")
        try:
            data_btn = self.page.wait_for_selector(
                'button:has-text("数据"), a:has-text("数据"), div:has-text("数据")',
                timeout=10000
            )
            data_btn.click()
            self._human_delay(1000, 2000)
            self._human_scroll()

            data = {
                "阅读量": "0",
                "收藏量": "0",
                "追读率": "0%",
                "完读率": "0%",
                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            all_texts = self.page.inner_text().split("\n")
            for i, text in enumerate(all_texts):
                text = text.strip()
                if "阅读" in text and i+1 < len(all_texts):
                    data["阅读量"] = all_texts[i+1].strip()
                elif "收藏" in text and i+1 < len(all_texts):
                    data["收藏量"] = all_texts[i+1].strip()
                elif "追读" in text and i+1 < len(all_texts):
                    data["追读率"] = all_texts[i+1].strip()
                elif "完读" in text and i+1 < len(all_texts):
                    data["完读率"] = all_texts[i+1].strip()

            log.success(f"【{self.platform}】爬取数据成功！{data}")
            return data
        except Exception as e:
            log.error(f"【{self.platform}】爬取数据失败: {e}")
            return {
                "阅读量": "0",
                "收藏量": "0",
                "追读率": "0%",
                "完读率": "0%",
                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }