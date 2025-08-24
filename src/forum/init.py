from flask import Blueprint

forum_bp=Blueprint(
    "forum",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/forum-static"
)

from .import routes