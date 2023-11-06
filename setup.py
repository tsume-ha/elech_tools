from distutils.core import setup

setup(
    name="elech_tools",
    version="0.1",
    description="Electrochemical data converter and analyser by python.",
    author="tsuhe-ha",
    author_email="50492756+tsume-ha@users.noreply.github.com",
    url="https://github.com/tsume-ha/elech_tools.git",
    install_requires=["numpy", "matplotlib", "pandas", "scipy"],
    package_dir={"": "src"},
)
