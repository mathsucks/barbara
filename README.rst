# barbara
Environment variable management

## Installation

```shell
$ pip install barbara
```

## Usage

  1. Create an `.env.template` for your project
      #### `.env.template`
      ```env
      DATABASE_HOST=127.0.0.1
      COMPLEX_KEY=[username:user]:[password:pass]@$DATABASE_HOST
      ```
  1. Run `barb` and you'll be prompted for the values
     ```bash
     $ barb
     .env does not exist. Create it? [y/N]: y
     Creating environment: .env
     Skip Existing: True
     COMPLEX_KEY:
     username [user]:
     password [pass]: wordpass
     DATABASE_HOST [127.0.0.1]:
     Environment ready!
     ```
  1. Inspect the generated file, see your values!
     ```
     $ cat .env
     COMPLEX_KEY=user:wordpass@$DATABASE_HOST
     DATABASE_HOST=127.0.0.1
     ```
     
## Subvariables

*Subvariables* work by using the `[variable_name:variable_default]` syntax within an `.env` template. 
You can use as many as you wish in a row, but they cannot be nested.

## Why `barbara`?

Because [Barbara Liskov](https://en.wikipedia.org/wiki/Barbara_Liskov) created the [Liskov Substituion Principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle) and is a prolific contributor to computer science and software engineering. Barbara is one of the Newton's metaphorical giants that enables us to see further. I humbly dedicate my project to her and her contributions and offer this project to its consumers with a license befitting that dedication.
