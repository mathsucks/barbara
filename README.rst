.. image:: https://repository-images.githubusercontent.com/131429006/7eb3f680-8572-11e9-8c3d-68b1476c50e8#

|python| |downloads| |license| |version|

Environment variable management

New in 2.0!
-----------

- Features have been dropped:
  - Legacy templates aren't supported anymore
  - Subvariables aren't supported anymore
  - SSM support has been dropped, as there are better ways to do this

- Schema-version has been added to document schema to make it easier for me to deprecate and change the schema if necessary

Installation
------------

.. code:: shell

    $ pip install barbara

Usage
-----

YAML Format (.env.yml)
----------------------

1. Create an ``.env.yml`` for your project

.. code:: yaml

   schema-version: 2
   project:
     name: your_project
     output: env-file

   environment:
     ENVIRONMENT_NAME: development
     DATABASE_URL: postgres://root@db:5432/mydb
     DEBUG: 1
     MEDIA_DIRS: media,static
     CSRF_COOKIE_SECURE: 0



2. Run ``barb`` and you'll be prompted for the values

.. code:: bash

   $ barb
   env-file does not exist. Create it? [y/N]: y
   Creating environment: env-file
   Skip Existing: True
   DATABASE_URL:
   user [root]:
   password [root]: wordpass
   host [127.0.0.1]:
   port [5432]:
   db_name [sample]:
   ENVIRONMENT_NAME [development]:
   Environment ready!

3. Inspect the generated file, see your values!

.. code:: bash

   $ cat .env
   DATABASE_URL=root:wordpass@127.0.0.1:5432/sample
   ENVIRONMENT_NAME=development


Why ``barbara``?
----------------

Because `Barbara Liskov <https://en.wikipedia.org/wiki/Barbara_Liskov>`__ created the `Liskov Substitution
Principle <https://en.wikipedia.org/wiki/Liskov_substitution_principle>`__ and is a prolific contributor to
computer science and software engineering. Barbara is one of the Newton's metaphorical giants that enables us
to see further. I humbly dedicate my project to her and her contributions and offer this project to its
consumers with a license befitting that dedication.



.. |python| image:: https://img.shields.io/pypi/pyversions/barbara.svg?logo=python&logoColor=yellow&style=for-the-badge
.. |downloads| image:: https://img.shields.io/pypi/dm/barbara.svg?style=for-the-badge
.. |license| image:: https://img.shields.io/pypi/l/barbara.svg?style=for-the-badge
.. |version| image:: https://img.shields.io/pypi/v/barbara.svg?style=for-the-badge
