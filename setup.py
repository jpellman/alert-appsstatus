from setuptools import setup

setup(
    name="alert-appsstatus",
    version="0.9.0",
    url="https://github.com/jpellman/alert-appsstatus",
    download_url="https://github.com/jpellman/alert-appsstatus/archive/master.zip",
    author="John Pellman",
    author_email="monkeybrain@libjpel.so",
    description="A Python script that parses the Google Apps Status Dashboard RSS feed and sends out e-mail alerts.",
    py_modules=["alert_appsstatus"],
    entry_points={
        "console_scripts": ["alert-appsstatus = alert_appsstatus:main"]
    },
    install_requires=[
        "pyyaml",
        "requests",
        "feedparser",
        "psutil"
    ]
)
