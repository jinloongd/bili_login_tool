# bili_login_tool

> A tool to get [bilibili](https://www.bilibili.com/)'s access token and refresh token.

## System Requirements

- [Python](https://www.python.org/) 3.6 or newer version

## Usage

```shell
# Step 1. Install requirements by pip 
pip install -r requirements.txt
# Step 2. Run main.py then follow the prompts
python main.py
```

## Package by [Pyinstaller](https://www.pyinstaller.org/)

```shell
pyinstaller bili_login_tool.spec
# or
pyinstaller -i assets/bilibili.ico -F main.py
```

## References

- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)
