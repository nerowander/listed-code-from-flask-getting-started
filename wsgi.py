import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__),'.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 有需要可以加上测试的代码

