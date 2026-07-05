#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""StarsailX 启动入口。"""
from starsailx.startup import prepare_runtime
from starsailx.app import run_app


def main() -> None:
    prepare_runtime()
    run_app()


if __name__ == "__main__":
    main()
