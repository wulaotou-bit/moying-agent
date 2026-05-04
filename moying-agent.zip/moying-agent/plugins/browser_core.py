"""
墨影浏览器核心模块
功能：
1. 防检测浏览器初始化
2. AES加密Cookie持久化
3. 自动加载/保存Cookie
"""
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from config import Config
from utils.logger import log
import json
import base64
from cryptography.fernet import Fernet

class BrowserCore:
    def __init__(self, platform: str = "fanqie"):
        self.platform = platform
        self.cookie_path = Config.COOKIE_DIR / f"{platform}_cookies.json"
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

    def _get_cipher(self):
        """用账号密码生成AES密钥，不存储密钥"""
        account = Config.PLATFORM_ACCOUNTS[self.platform]
        key_material = (account["user"] + account["pwd"]).encode()[:32].ljust(32, b'0')
        key = base64.urlsafe_b64encode(key_material)
        return Fernet(key)

    def init_browser(self):
        """初始化防检测浏览器"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=Config.BROWSER_HEADLESS,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN"
        )
        self.page = self.context.new_page()
        stealth_sync(self.page)  # 隐藏自动化特征
        log.info(f"【{self.platform}】防检测浏览器初始化完成")

    def load_cookies(self) -> bool:
        """加载加密Cookie"""
        if not self.cookie_path.exists():
            return False
        try:
            cipher = self._get_cipher()
            with open(self.cookie_path, "rb") as f:
                encrypted_cookies = f.read()
            cookies = json.loads(cipher.decrypt(encrypted_cookies).decode())
            self.context.add_cookies(cookies)
            log.info(f"【{self.platform}】加密Cookie加载成功")
            return True
        except Exception as e:
            log.warning(f"【{self.platform}】Cookie加载失败: {e}")
            return False

    def save_cookies(self):
        """加密保存Cookie"""
        try:
            cipher = self._get_cipher()
            cookies = self.context.cookies()
            encrypted = cipher.encrypt(json.dumps(cookies, ensure_ascii=False).encode())
            with open(self.cookie_path, "wb") as f:
                f.write(encrypted)
            log.info(f"【{self.platform}】Cookie已AES加密保存")
        except Exception as e:
            log.error(f"【{self.platform}】Cookie保存失败: {e}")

    def close(self):
        """安全关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        log.info(f"【{self.platform}】浏览器已安全关闭")