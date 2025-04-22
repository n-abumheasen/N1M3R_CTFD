import argparse
import os
from gevent import monkey

# إعدادات البرامتر
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="Port for debug server to listen on", default=4000)
parser.add_argument(
    "--profile", help="Enable flask_profiler profiling", action="store_true"
)
parser.add_argument(
    "--disable-gevent",
    help="Disable importing gevent and monkey patching",
    action="store_false",
)
args = parser.parse_args()

# إذا كان --disable-gevent مفعلاً
if args.disable_gevent:
    print(" * Importing gevent and monkey patching. Use --disable-gevent to disable.")
    monkey.patch_all()

# استيراد التطبيق
from CTFd import create_app

# إنشاء التطبيق
app = create_app()

# إضافة دعم profiling إذا كان مفعلاً
if args.profile:
    from flask_debugtoolbar import DebugToolbarExtension
    import flask_profiler

    app.config["flask_profiler"] = {
        "enabled": app.config["DEBUG"],
        "storage": {"engine": "sqlite"},
        "basicAuth": {"enabled": False},
        "ignore": ["^/themes/.*", "^/events"],
    }
    flask_profiler.init_app(app)
    app.config["DEBUG_TB_PROFILER_ENABLED"] = True
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)
    print(" * Flask profiling running at http://127.0.0.1:4000/flask-profiler/")

# تحقق من إذا كنت تعمل مع gunicorn أو لا
if __name__ == "__main__":
    # إذا كانت البيئة تستخدم gunicorn، لا نحتاج إلى app.run
    if os.environ.get("GUNICORN_CMD_ARGS"):
        # تأكد من أن gunicorn يقوم بتشغيله
        print("Running with gunicorn")
    else:
        # في حالة تشغيل التطبيق محليًا (أو غير gunicorn)
        app.run(debug=True, threaded=True, host="127.0.0.1", port=args.port)
