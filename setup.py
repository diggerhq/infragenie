from setuptools import setup



setup(
    name='InfraGenie CLI',
    # package_dir={
    #     'diggercli': ''
    # },
    install_requires=[
        "python-hcl2==3.0.1",
        "click==7.1.2",
        "rich==10.9.0",
    ],
    version="1.0",
    py_modules=["infragenie",],
    packages=['infragenie', ],
    entry_points='''
        [console_scripts]
        igm=infragenie.genie:cli
    '''
)
