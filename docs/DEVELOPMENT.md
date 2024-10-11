# :building_construction: Development Instructions

## :books: Table of Contents

- [Installation](#construction_worker-getting-started)
    - [With docker](#construction-with-docker)
    - [Manually](#wheelchair-manually)
        - [requirements](#with-requirements)
        - [poetry](#with-poetry)
    - [Localization](#globe_with_meridians-i18n)
- [Tests](#test_tube-tests)

## :construction_worker: Getting Started

### :construction: With docker

First, rename the file `.env.dist` to `.env`.\
Afterward, fill it with the required data.

| Variable             | Type | Importance | Description                                     |
|----------------------|------|------------|-------------------------------------------------|
| BOT_TOKEN            | str  | True       | Bot token                                       |
| ADMINS               | list | True       | list of admins id                               |
| SUPPORTS             | list | True       | list of supports id                             |
| TIMEZONE             | str  | True       | your time zone for working with the scheduler   |
| MODERATE_CHAT        | str  | True       | telegram chat where the event will be moderated |
| SIGNATURE_SECRET_KEY | str  | True       | signature for login                             |
| USE_REDIS            | bool | True       | Use redis or default storage                    |

Once done, run the following command:

```shell
$ docker-compose build
```

### :wheelchair: Manually

If you prefer not to use Docker, you can manually build the app.
Before installing the DatingBot project, ensure Python is installed:

```sh
$ python -V
```

If Python is installed, clone the DatingBot repository:

```sh
$ git clone https://github.com/DavidRomanovizc/DatingBot.git
```

Create a virtual environment:

```sh
$ python -m venv venv
```

Activate the virtual environment:

<u>On Windows:</u>

```sh
$ venv\Scripts\activate
```

<u>On macOS and Linux:</u>

```sh
$ source venv/bin/activate
```

#### with requirements

```shell
$ pip install -r requirements.txt
```

#### with poetry

After setting up the virtual environment, install Poetry with pip:

```shell
$ pip install poetry
```

Then install Poetry dependencies:

```shell
poetry install
```

## :globe_with_meridians: i18n

### Title - dating

#### Launching for the first time

1. Extract texts from files (he finds it himself)
   ```sh
   $ pybabel extract -F babel.cfg --input-dirs=. -o locales/messages.pot
   ```
2. Create a folder for English translation
   ```sh
   $ pybabel init -i locales/messages.pot -d locales -D messages -l en
   ```
3. For Russian translation
   ```sh
   $ pybabel init -i locales/messages.pot -d locales -D messages -l ru
   ```
4. Translate and compile
   ```sh
   $ pybabel compile -d locales -D messages
   ```

#### Updating translations

1. Extract texts from files, add text to translated versions
   ```sh
   $ pybabel extract -F babel.cfg -o locales/messages.pot .
   $ pybabel update -d locales -D dating -i locales/messages.pot
   ```
2. Manually translate, then compile
   ```sh
   $ pybabel compile -d locales -D messages
   ```

## :test_tube: Tests