barbara
=======

Environment variable management

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

   project: your_project

   environment:
     ENVIRONMENT_NAME: development
     DATABASE_URL:
       template: "{user}:{password}@{host}:{port}/{db_name}"
       subvariables:
           user: root
           password: root
           host: 127.0.0.1
           port: 5432
           db_name: sample


2. Run ``barb`` and you'll be prompted for the values

.. code:: bash

   $ barb
   .env does not exist. Create it? [y/N]: y
   Creating environment: .env
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

Subvariables
------------

*Subvariables* work by using the following syntax:

.. code:: yaml

   VARIABLE_NAME:
     template: "{subvariable1} {subvariable2}"
     subvariables:
       subvariable1: default value for subvariable 1
       subvariable2: default value for subvariable 2

For the given example, the user is shown ``VARIABLE_NAME`` as a title, and then prompted for the two values and offered
a default value. Any subvariable that appears in the template must also appear in the subvariables dictionary or the
string formatting operation will fail. Python string template syntax is used and formatting can be applied using the
standard colon syntax.


Advanced Usage (AWS SSM)
------------------------

.. note:: You must create the values in AWS SSM before they can be retrieved. You will also need the correct IAM
          permissions to retrieve the values from AWS. All values are assumed to be encrypted at rest.

1. Create an ``.env.yml`` for your project with the ``deployments`` section. This section is a declarative heirarchy
   of overrides. At the root of deployments is the most general and therefore the lowest priority. For reference, the
   paths have been provided as comments and are not required in practice.

.. code:: yaml

   project: your_project

   environment:
     DEBUG: 1
     ENVIRONMENT_NAME: development
     DATABASE_URL:
       template: "{user}:{password}@{host}:{port}/{db_name}"
       subvariables:
           user: root
           password: root
           host: 127.0.0.1
           port: 5432
           db_name: sample
     HOST_TYPE: local

   deployments:
     - DEBUG                 # /your_project/DEBUG
     - staging:
       - DATABASE_URL        # /your_project/staging/DATABASE_URL
       - ENVIRONMENT_NAME    # /your_project/staging/ENVIRONMENT_NAME
       - app_server:
         - HOST_TYPE         # /your_project/staging/app_server/HOST_TYPE
       - worker:
         - HOST_TYPE         # /your_project/staging/worker/HOST_TYPE
     - production:
       - DATABASE_URL        # /your_project/production/DATABASE_URL
       - ENVIRONMENT_NAME    # /your_project/production/ENVIRONMENT_NAME
       - app_server:
         - HOST_TYPE         # /your_project/production/app_server/HOST_TYPE
       - worker:
         - HOST_TYPE         # /your_project/production/worker/HOST_TYPE

2. Run ``barb-deploy -p /your_project/staging/app_server/`` and a new ``.env`` will be produced using that search path
   to determine the override priority of each variable.

.. code:: bash

   $ barb-deploy -p /your_project/staging/app_server/
   Creating environment: .env (using search_path: /your_project/staging/app_server/)
   Environment ready!

3. Inspect the generated file, see your values!

.. code:: bash

   $ cat .env
   DATABASE_URL=postgres://staging:staging@localhost:5432/staging_db
   DEBUG=0
   ENVIRONMENT_NAME=staging
   HOST_TYPE=app_server



Legacy Format (.env.template)
-----------------------------

1. Create an ``.env.template`` for your project

.. code:: ini

   DATABASE_HOST=127.0.0.1
   COMPLEX_KEY=[username:user]:[password:pass]@$DATABASE_HOST


2. Run ``barb`` and you'll be prompted for the values

.. code:: bash

   $ barb
   .env does not exist. Create it? [y/N]: y
   Creating environment: .env
   Skip Existing: True
   COMPLEX_KEY:
   username [user]:
   password [pass]: wordpass
   DATABASE_HOST [127.0.0.1]:
   Environment ready!


3. Inspect the generated file, see your values!

.. code:: bash

   $ cat .env
   COMPLEX_KEY=user:wordpass@$DATABASE_HOST
   DATABASE_HOST=127.0.0.1

*Legacy subvariables* work by using the ``[variable_name:variable_default]`` syntax within an ``.env`` template. You
can use as many as you wish in a row, but they cannot be nested.


Why ``barbara``?
----------------

Because `Barbara Liskov <https://en.wikipedia.org/wiki/Barbara_Liskov>`__ created the `Liskov Substitution
Principle <https://en.wikipedia.org/wiki/Liskov_substitution_principle>`__ and is a prolific contributor to
computer science and software engineering. Barbara is one of the Newton's metaphorical giants that enables us
to see further. I humbly dedicate my project to her and her contributions and offer this project to its
consumers with a license befitting that dedication.
