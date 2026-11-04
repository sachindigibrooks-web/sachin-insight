"""JavaScript rendering: load pages in a real (headless) browser, like Google does.

Sites built with React, Vue, Next.js and similar put their content, links and
even titles into the page with JavaScript, so the raw HTML looks empty. With
rendering on, every internal page is also opened in Chromium and the final
HTML is what gets checked.

The browser already on the PC is used when possible (Microsoft Edge ships with
Windows, Chrome is common on Macs), so nothing big has to be downloaded. Only
if neither is found is Playwright's Chromium downloaded, once.
"""

import asyncio
import os
import subprocess

# Images, video and fonts don't change the HTML; skipping them makes rendering much faster.
SKIP = {"image", "media", "font"}


class RenderError(Exception):
    pass


class Renderer:
    def __init__(self, user_agent, concurrency=3, timeout=20.0):
        self.user_agent = user_agent
        self.slots = asyncio.Semaphore(max(1, min(concurrency, 4)))
        self.timeout = timeout
        self.browser_name = None

    async def start(self):
        from playwright.async_api import async_playwright
        self.pw = await async_playwright().start()
        errors = []
        exe = os.environ.get("SEO_CHROMIUM")  # explicit path (tests, unusual setups)
        attempts = ([("custom", {"executable_path": exe})] if exe else []) + [
            ("Microsoft Edge", {"channel": "msedge"}),
            ("Google Chrome", {"channel": "chrome"}),
            ("Chromium", {}),
        ]
        for name, kw in attempts:
            try:
                self.browser = await self.pw.chromium.launch(headless=True, **kw)
                self.browser_name = name
                break
            except Exception as e:
                errors.append(f"{name}: {str(e).splitlines()[0][:120]}")
        else:
            if not await asyncio.to_thread(install_chromium):
                await self.pw.stop()
                raise RenderError("No browser found for JavaScript rendering. Install Google "
                                  "Chrome or Microsoft Edge. (" + "; ".join(errors) + ")")
            self.browser = await self.pw.chromium.launch(headless=True)
            self.browser_name = "Chromium"
        self.context = await self.browser.new_context(user_agent=self.user_agent)
        await self.context.route("**/*", self._route)

    async def _route(self, route):
        if route.request.resource_type in SKIP:
            await route.abort()
        else:
            await route.continue_()

    async def render(self, url):
        """The page's HTML after its JavaScript ran (or raise RenderError)."""
        async with self.slots:
            page = await self.context.new_page()
            try:
                try:
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
                except Exception as e:
                    if "Timeout" not in type(e).__name__ and "Timeout" not in str(e):
                        raise RenderError(str(e).splitlines()[0][:200])
                    # Pages that keep polling never go idle; use what has loaded so far.
                return await page.content()
            finally:
                await page.close()

    async def stop(self):
        for close in (getattr(self, "context", None), getattr(self, "browser", None)):
            try:
                if close:
                    await close.close()
            except Exception:
                pass
        try:
            await self.pw.stop()
        except Exception:
            pass


def install_chromium():
    """Download Playwright's Chromium (about 150 MB, once). Returns True when it worked."""
    try:
        from playwright._impl._driver import compute_driver_executable, get_driver_env
        driver = compute_driver_executable()
        cmd = list(driver) if isinstance(driver, tuple) else [str(driver)]
        flags = 0x08000000 if os.name == "nt" else 0  # no console window
        r = subprocess.run(cmd + ["install", "chromium"], env=get_driver_env(),
                           capture_output=True, timeout=900, creationflags=flags)
        return r.returncode == 0
    except Exception:
        return False
