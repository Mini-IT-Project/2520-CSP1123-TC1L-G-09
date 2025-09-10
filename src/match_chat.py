from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db

MatchChat_bp = Blueprint("MatchChat",__name__)

@MatchChat_bp.route('/')
def home():
    return render_template("MatchChat.html")