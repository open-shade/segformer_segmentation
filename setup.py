from setuptools import setup

package_name = '<name>'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
        'setuptools',
        'transformers',
        'torch',
        'cython',
        'datasets',
        "Pillow",
        'charset-normalizer==2.0.0',
        'packaging==20.9',
        'numpy==1.23.0',
        'opencv-python'
    ],
    zip_safe=True,
    maintainer='lidar',
    maintainer_email='lidar@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            '<name> = <name>.<name>:main'
        ],
    },
)
