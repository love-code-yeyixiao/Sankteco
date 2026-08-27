from setuptools import setup, find_packages

setup(
    name="plugin_template",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "sankteco.plugin": [  # 这是我们的命名空间
            "plugin_template = plugin_template.main:register",  # 格式: '插件ID = 模块路径:函数名'
        ]
    },
    install_requires=[
        "stevedore",  # 插件开发者也需要安装 stevedore
        # 其他依赖，比如 'requests', 'pydub' 等，可以在这里自由声明！
    ],
)
