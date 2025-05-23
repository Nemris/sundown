# sundown
Sundown is a way to interface with DeviantArt's Eclipse API normally used by browsers, which doesn't
need authentication. Requests are made asynchronously for improved performance.

## Requirements

The requirements to use Sundown in your project are:
 * [aiohttp];
 * [beautifulsoup4].

If you want to _contribute_ to this module, you'll also need to use [Poetry] to manage your
environment, and the following dependencies:
 * [black];
 * [hypothesis];
 * [pylint];
 * [pytest].

## Installation

At the moment, Sundown isn't distributed on any remote repository.

To obtain a wheel you can then install, you need to clone this repository. Checkout to the commit
or tag you wish, then use Poetry and run:

```bash
poetry build -f wheel
```

## Features

At the moment, Sundown supports only the following:
 * basic deviation metadata such as URLs and IDs;
 * comment pages and comments.

### Why not use the official DA API?

This project's ancestor was built out of the necessity of obtaining and using comment links
contained in comments. The official API wasn't usable for this purpose, as it abstracted away links
behind methods and UUIDs.

In other words - unless you have a specific need involving comment links, this module is probably
not what you're looking for.

## Contributing

Since this is mainly an internal module that was spun off, it's highly unlikely that I'll implement
new features unless my other projects require them. Nevertheless, I'll be grateful for any
contributions.

To setup a virtual environment with the required dependencies, you will need to run:

```bash
poetry install
```

**PRs produced as a result of "vibe coding" will be rejected.**

## Code style

Sundown follows the Black code style, except for when doing so would result in lines being crammed
into one, as might happen e.g. in list comprehensions and similar constructs. If in doubt, follow
your own gut instinct and look at the existing code.

Remember to type-annotate all parameters and returned values, and always add docstrings to public
code.
While test strategies are best with a docstring each, test modules and functions do not need them,
provided the test names themselves are descriptive.

This project follows composition over inheritance, except for the exception hierarchy.

### Linting and testing

Before opening a PR, ensure that your code is linted with Pylint. If you need to disable a warning,
for example in case of false positives, leave a comment explaining your reasoning or mention it in
the PR.

To write your tests, refer to Hypothesis' docs and to the available examples. I'll appreciate it if
you'll add tests for every nontrivial method.

## License

This module is licensed under the terms of the [MIT] license.

Check [LICENSE] for further info.

[poetry]:https://python-poetry.org

[aiohttp]:https://docs.aiohttp.org/en/stable/index.html
[beautifulsoup4]:https://beautiful-soup-4.readthedocs.io/en/latest/

[black]:https://black.readthedocs.io/en/stable/index.html
[hypothesis]:https://hypothesis.readthedocs.io/en/latest/
[pylint]:https://pylint.readthedocs.io/en/stable/
[pytest]:https://pytest.org/

[MIT]:https://choosealicense.com/licenses/mit/
[LICENSE]:./LICENSE
