
import os
import signal
import subprocess
import time
from pathlib import Path

from database.bots import (
    get_bot,
    update_bot_pid,
    clear_bot_pid
)


# نگهداری پردازش‌هایی که همین اجرای ربات مادر ساخته است
# تا بتوانیم بعداً آن‌ها را با wait جمع‌آوری کنیم.
_CHILD_PROCESSES = {}


def _get_process_info(pid):
    """
    اطلاعات پردازش را از /proc دریافت می‌کند.
    وضعیت Z یعنی Zombie و X یعنی Dead.
    """
    try:
        proc_path = Path(f"/proc/{pid}")

        if not proc_path.exists():
            return None

        cmdline = (proc_path / "cmdline").read_bytes()

        args = [
            arg.decode(errors="replace")
            for arg in cmdline.split(b"\0")
            if arg
        ]

        stat_text = (proc_path / "stat").read_text()

        # نام پردازش ممکن است فاصله یا پرانتز داشته باشد.
        stat_fields = stat_text[stat_text.rfind(")") + 2:].split()

        state = stat_fields[0]
        process_group = os.getpgid(pid)

        return args, process_group, state

    except (ProcessLookupError, FileNotFoundError, PermissionError):
        return None


def _is_managed_process(bot):
    """
    بررسی می‌کند PID واقعاً متعلق به فایل اصلی همین ربات باشد.
    """
    pid = bot["pid"]

    if not pid:
        return False

    info = _get_process_info(pid)

    if info is None:
        return False

    args, process_group, state = info

    # پردازش Zombie یا Dead در حال اجرا محسوب نمی‌شود.
    if state in ("Z", "X"):
        return False

    script_path = str(
        (Path(bot["project_path"]) / bot["entry_file"]).resolve()
    )

    return script_path in args and process_group == pid


def _reap_child(bot_id):
    """
    اگر پردازش فرزند تمام شده باشد، آن را با poll جمع‌آوری می‌کند.
    """
    process = _CHILD_PROCESSES.get(bot_id)

    if process is None:
        return

    if process.poll() is not None:
        _CHILD_PROCESSES.pop(bot_id, None)


def is_running(bot_id):
    """
    وضعیت واقعی ربات را بررسی می‌کند.
    """
    _reap_child(bot_id)

    bot = get_bot(bot_id)

    if bot is None or bot["pid"] is None:
        return False

    if _is_managed_process(bot):
        return True

    clear_bot_pid(bot_id)
    return False


def start_bot(bot_id):
    bot = get_bot(bot_id)

    if bot is None:
        return False, "ربات پیدا نشد."

    if is_running(bot_id):
        return False, "ربات از قبل در حال اجراست."

    project_path = Path(bot["project_path"]).resolve()
    venv_path = Path(bot["venv_path"]).resolve()

    python_path = venv_path / "bin" / "python"
    script_path = (project_path / bot["entry_file"]).resolve()

    # جلوگیری از اجرای فایل خارج از پوشه پروژه
    if not script_path.is_relative_to(project_path):
        return False, "مسیر فایل اصلی نامعتبر است."

    if not python_path.is_file():
        return False, "Python محیط مجازی پیدا نشد."

    if not script_path.is_file():
        return False, "فایل اصلی ربات پیدا نشد."

    log_path = bot["log_path"]

    if not log_path:
        log_path = project_path / "bot.log"
    else:
        log_path = Path(log_path).resolve()

    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Do not pass the mother bot's credentials to managed bots.
        # The child bot must load BOT_TOKEN from its own project .env.
        child_env = os.environ.copy()
        child_env.pop("BOT_TOKEN", None)
        child_env.pop("ADMIN_ID", None)

        with open(log_path, "a", encoding="utf-8") as log_file:
            process = subprocess.Popen(
                [str(python_path), str(script_path)],
                cwd=str(project_path),
                env=child_env,
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True
            )

        # نگهداری شیء Popen برای wait کردن هنگام توقف
        _CHILD_PROCESSES[bot_id] = process

        # بررسی می‌کنیم پردازش بلافاصله کرش نکرده باشد.
        time.sleep(0.5)

        if process.poll() is not None:
            _CHILD_PROCESSES.pop(bot_id, None)

            return False, (
                "ربات اجرا شد اما بلافاصله متوقف شد. "
                "لاگ را بررسی کنید."
            )

        update_bot_pid(bot_id, process.pid)

        return True, f"ربات با PID {process.pid} اجرا شد."

    except Exception as error:
        return False, f"خطا در اجرای ربات: {error}"


def stop_bot(bot_id):
    bot = get_bot(bot_id)

    if bot is None:
        return False, "ربات پیدا نشد."

    if not is_running(bot_id):
        return False, "ربات در حال اجرا نیست."

    # اطلاعات را دوباره می‌خوانیم چون is_running ممکن است
    # PID قدیمی را از دیتابیس پاک کرده باشد.
    bot = get_bot(bot_id)
    pid = bot["pid"]

    process = _CHILD_PROCESSES.get(bot_id)

    try:
        if not _is_managed_process(bot):
            clear_bot_pid(bot_id)
            return False, "پردازش معتبر ربات پیدا نشد."

        # فقط گروه پردازشی متعلق به همین ربات متوقف می‌شود.
        os.killpg(pid, signal.SIGTERM)

        if process is not None:
            try:
                # منتظر پایان پردازش می‌مانیم و آن را جمع‌آوری می‌کنیم.
                process.wait(timeout=10)

            except subprocess.TimeoutExpired:
                # اگر در ۱۰ ثانیه متوقف نشد، توقف اجباری
                os.killpg(pid, signal.SIGKILL)

                try:
                    process.wait(timeout=3)

                except subprocess.TimeoutExpired:
                    return False, "توقف پردازش پس از SIGKILL تأیید نشد."

            finally:
                if process.poll() is not None:
                    _CHILD_PROCESSES.pop(bot_id, None)

            clear_bot_pid(bot_id)
            return True, "ربات با موفقیت متوقف شد."

        # اگر ربات قبل از اجرای فعلی مادر روشن شده باشد،
        # شیء Popen آن در حافظه موجود نیست.
        deadline = time.monotonic() + 10

        while time.monotonic() < deadline:
            if not _is_managed_process(bot):
                clear_bot_pid(bot_id)
                return True, "ربات با موفقیت متوقف شد."

            time.sleep(0.25)

        # توقف اجباری در صورت نیاز
        if _is_managed_process(bot):
            os.killpg(pid, signal.SIGKILL)

        deadline = time.monotonic() + 3

        while time.monotonic() < deadline:
            if not _is_managed_process(bot):
                clear_bot_pid(bot_id)
                return True, "ربات به‌صورت اجباری متوقف شد."

            time.sleep(0.25)

        return False, "توقف ربات تأیید نشد."

    except ProcessLookupError:
        if process is not None:
            process.poll()
            _CHILD_PROCESSES.pop(bot_id, None)

        clear_bot_pid(bot_id)
        return True, "ربات قبلاً متوقف شده بود."

    except PermissionError:
        return False, "دسترسی لازم برای توقف ربات وجود ندارد."

    except Exception as error:
        return False, f"خطا در توقف ربات: {error}"


def restart_bot(bot_id):
    bot = get_bot(bot_id)

    if bot is None:
        return False, "ربات پیدا نشد."

    if is_running(bot_id):
        stopped, message = stop_bot(bot_id)

        if not stopped:
            return False, message

    return start_bot(bot_id)
