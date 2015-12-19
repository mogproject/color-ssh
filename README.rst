=========
color-ssh
=========

Runs remote commands, colorfully.

.. image:: https://badge.fury.io/py/color-ssh.svg
   :target: http://badge.fury.io/py/color-ssh
   :alt: PyPI version

.. image:: https://travis-ci.org/mogproject/color-ssh.svg?branch=master
   :target: https://travis-ci.org/mogproject/color-ssh
   :alt: Build Status

.. image:: https://coveralls.io/repos/mogproject/color-ssh/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/mogproject/color-ssh?branch=master
   :alt: Coverage Status

.. image:: https://img.shields.io/badge/license-Apache%202.0-blue.svg
   :target: http://choosealicense.com/licenses/apache-2.0/
   :alt: License

.. image:: https://badge.waffle.io/mogproject/color-ssh.svg?label=ready&title=Ready
   :target: https://waffle.io/mogproject/color-ssh
   :alt: 'Stories in Ready'

--------
Features
--------

* todo

------------
Dependencies
------------

* Python: 2.6 / 2.7 / 3.2 / 3.3 / 3.4 / 3.5

------------
Installation
------------

* ``pip`` command may need ``sudo``

+-------------------------+---------------------------------------+
| Operation               | Command                               |
+=========================+=======================================+
| Install                 |``pip install color-ssh``              |
+-------------------------+---------------------------------------+
| Upgrade                 |``pip install --upgrade color-ssh``    |
+-------------------------+---------------------------------------+
| Uninstall               |``pip uninstall color-ssh``            |
+-------------------------+---------------------------------------+
| Check installed version |``color-ssh --version``                |
+-------------------------+---------------------------------------+
| Help                    |``color-ssh -h``                       |
+-------------------------+---------------------------------------+

----------
Quickstart
----------

Two commands will be installed.

* color-cat

::

    echo abc | color-cat -l label
    echo abc | color-cat -l label -c magenta
    color-cat -l label README.rst

* color-ssh

::

    color-ssh server-1 ls -l
    color-ssh server-1 'cd /tmp && pwd'
    color-ssh --ssh 'ssh -v' username@server-1 id
