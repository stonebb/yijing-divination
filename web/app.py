#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""易经算卦 Web 应用 — Flask 后端"""

import json
import os
import sys

# Ensure parent directory in path so we can import yijing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, render_template, request

from yijing import HexagramDatabase, DivinationEngine, ResultInterpreter

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

db = HexagramDatabase()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/divine", methods=["POST"])
def divine():
    data = request.get_json() or {}
    method = data.get("method", "coin")
    question = data.get("question", "").strip()
    seed = data.get("seed")

    if method not in ("coin", "digital", "time"):
        return jsonify({"error": f"未知方法: {method}"}), 400

    engine = DivinationEngine(seed=seed)
    if method == "coin":
        lines = engine.toss_coins()
    elif method == "digital":
        lines = engine.digital_method()
    else:
        lines = engine.time_method()

    interpreter = ResultInterpreter(db)
    result = interpreter.interpret(lines, question)

    return jsonify({
        "lines": lines,
        "main_hexagram": result["main_hexagram"],
        "changing_hexagram": result["changing_hexagram"],
        "changing_positions": result["changing_positions"],
        "changing_yao_ci": result["changing_yao_ci"],
        "yao_drawing": result["yao_drawing"],
        "report": result["report"],
        "brief": interpreter.format_brief(result),
        "question": question,
    })


@app.route("/api/hexagrams")
def list_hexagrams():
    hs = []
    for h in db.hexagrams:
        hs.append({
            "id": h["id"],
            "name": h["name"],
            "short_name": h["short_name"],
            "unicode_symbol": h["unicode_symbol"],
            "upper_trigram": h["upper_trigram"],
            "lower_trigram": h["lower_trigram"],
            "core_meaning": h["core_meaning"],
            "keywords": h["keywords"],
        })
    return jsonify(hs)


@app.route("/api/hexagram/<int:hid>")
def get_hexagram(hid):
    h = db.get_by_id(hid)
    if not h:
        return jsonify({"error": "未找到卦象"}), 404
    return jsonify(h)


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    results = db.search_by_keyword(q)
    return jsonify([
        {
            "id": h["id"],
            "name": h["name"],
            "short_name": h["short_name"],
            "unicode_symbol": h["unicode_symbol"],
            "core_meaning": h["core_meaning"],
            "keywords": h["keywords"],
        }
        for h in results
    ])


@app.route("/api/random")
def random_hexagram():
    import random
    h = random.choice(db.hexagrams)
    return jsonify(h)


if __name__ == "__main__":
    print("易经算卦 Web 应用启动中...")
    print("访问: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
