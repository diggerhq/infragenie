from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='infragenie',
    author="Mohamed Habib",
    author_email="mo@digger.dev",
    description="decompose your terraform with dependency injection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "python-hcl2==3.0.1",
        "click==7.1.2",
        "rich==10.9.0",
    ],
    version="0.1.5",
    url="https://github.com/diggerhq/infragenie",
    py_modules=["infragenie",],
    packages=['infragenie', ],
    entry_points='''
        [console_scripts]
        igm=infragenie.genie:cli
    '''
)
