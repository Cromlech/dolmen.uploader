from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='dolmen.uploader',
      version=version,
      description="Uploading application/service",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      license='ZPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      namespace_packages=['dolmen'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          'WebOb',
          'js.jquery',
          'js.jqueryui',
      ],
      entry_points={
          'fanstatic.libraries': [
              'blueimp_upload = dolmen.uploader.resources.blueimp:library',
              'hayageek_upload = dolmen.uploader.resources.hayageek:library',
              ],
          'paste.app_factory': [
              'uploader = dolmen.uploader.service:upload_service',
              ],
          },
      )
