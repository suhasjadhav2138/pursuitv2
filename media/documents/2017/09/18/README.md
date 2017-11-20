# Boxer

Boxer framework is testing framework for rest based servers. Boxer gives you ability to write tests without writing
single line of code. Everything is configurable from suite/test configuration files. These files use [yaml](http://www.yaml.org/spec/1.2/spec.html)
file format. Although you don't need to write any code for tests you can embed python code into test files to make custom
test assertions.

#### Info ! 
Boxer is under development! API is stable now, no major bugs are found in current status. If you find any issue/bug/enhancement
feel free to open github issue.

# Design
First to mention is that boxer is heavily based on [vcontext](http://github.com/phonkee/vcontext) package. Please
read the documentation to vceontext and try to grasp it since it's fundamental knowledge to understand boxer.
All context data are during the test expanded (vcontext has now native support for expansion) so this brings us
a whole new level of creating test data.
Base context is created when boxer starts with some sane default values, and can be extended on multiple levels (cli, suite, test). 

Boxer concept is similar as can be found in other test frameworks:
* Suite - suite is a package of multiple tests
* Test - single test in suite
* Case - test can have multiple cases to perform (request list), cases are optional.

Suite is configured in configuratino file with file extension `boxersuite`, Test can be configured either in separate
file with `boxertest` extension or inlined in Suite configuration file, and cases (optional) are configured inline
in Test configuration. More about configuration later.

## How it works?

So how boxer runs my suites/tests? These are raw steps how boxer does testing:

* Read command line args and setup Boxer (logging, etc...)
* Create default context with environment (`env` key) and update it with boxer configuration (if passed to cli)
* Update this context with command line context
* Read and parse suites, clone boxer context and update it with suite configuration and store to suite
* find all tests (files) parse them, clone suite context update with test values and store to test
* read external data (if provided)
* parse cases (if provided)
* start testing
* expand context and test every expanded item for every case in test if given, otherwise make single request for every data items
* verify expects
* store data for report
* make report

## External data

Boxer has neat feature that you can specify test data in external sources.
This gives you really nice separation of test logic and tests. This external sources are easily configurable in test configuration
and use `vcontext.Context` key/value for defining data. Covered in [Datasource](#datasource)

## Context hierarchy
Context is inherited from the top to the bottom hierarchy (Default > boxer config > cli > suite > test > case). One important thing is
that when the context goes down with the hierarchy it is always cloned so you cannot alter context data from lower level
to upper level, e.g.: if you change context data in test, suite context will not be changed.

The hierarchy how context is inherited is following:
* Default context - context that is created by boxer with some sane default values and environment variables (`env`)
* Boxer config - configuration file passed as `--config` in boxer command (see [Boxer configuration](#boxer-configuration)
* Command line context values - you can specify context values directly from command line such as `boxer run --context key value --context key2 value2`
    which provides us nice way to set e.g. host value directly from command line `boxer run --context url.host localhost:9999`
* Suite configuration - suite configuration file can extend context
* Test configuration - test configuration file or inlined test in suite configuration

Boxer, when installed provides shell command `boxer` which offers multiple sub commands to use. To see all commands
please run:

    boxer --help

Main command that you'll use most of the time is `run`.


# Context variables

Every level (suite > test > case) has some context values that are configuring given component, and all other context data
you can use either to pass down the hierarchy (e.g. custom python code can leverage from that) and some data is passed directly
to rest http request.

Variables that are tight to actual http request are following:

* `url` - url components dictionary for rest request
    * `scheme` - request scheme such as http/https
    * `host` - host used for requests e.g. `localhost:9999`
    * `api_prefix` - common prefix for all http rest calls e.g. `/api/vi`
    * `query` - dictionary with GET query parameters, e.g. `query.action: "save"` adds ?action=save
    * `endpoint` - rest endpoint such as `cpe/12345`, this is interpolated (used as a template) so you can `replace` values in it
        e.g. if you have `cpe_mac = aaaa` in the context you can set endpoint to `cpe/{{cpe_mac}}` and it will yield to `cpe/aaaa`.
* `request` - various request related values dictionary
    * `method` - http method used e.g. `post`, `get` ...
    * `headers` - http request headers (can be used e.g. for authorization etc..)
    * `body` - body that will be sent in request (e.g. `request.body.user: "phonkee"` will send `{"user": "phonkee"}` as body of request
        if body is raw string, it's send untouched.
    * `gzip` - boolean, whether boxer should gzip `request.body`
    * `timeout` - timeout passed to send method
* `response` - access to `requests` response so it can be used in `expect` blocks which I will describe later.
    you can use it e.g. `response.json.status`
* `debug` - boolean value that enables `debug` function in `__python__` blocks print to stdout
* `session` - if you provide your own requests session, that session will be used. This feature comes handy, when you'll
    want provide https certificates

# Shared context

There are some cases where you need shared context across the whole run of boxer. That's impossible with context since
they are cloned (intentionally). For this case, all `__python__` blocks have access to variable `shared_context` which 
holds context where you can assign any data you want. Be careful that this context is not added to boxer context.
Also this context is not expanded. It's just for `__python__` blocks.


# Boxer configuration

Boxer can have base configuration in file and passed to boxer by `--config` command line argument.
Boxer has some specific configuration, all other values are passed as context values.

Configuration:
* `report` - dictionary with values for html report
* `python_locals` - multiline string, python code which symbols will be used in all `__python__` blocks within tests/suites.
    you can define custom functions, classes to be used later in tests.
    You need to decorate functions/classes with `export` decorator, so boxer understands what you want to export from locals.
* `required_version` - you can specify version of boxer for given test suites. Example: `>=1.0.0`

#### `python_locals`

`python_locals` is custom code block where you can define functions/classes that will be available across
all `__python__` blocks. To achieve this, you need to decorate those symbols with `@export` decorator.
Also there is possibility to run custom code that will be run before any suite is run. That's also
why boxer injects there exception `ImproperlyConfigured`. If this exception is raised, boxer stops its
execution with given error message. Also to distinguish the code that will be run on import (on start) 
you can use pythons construction `if __name__ == "__main__"` (boxer injects `__name__` variable).

this block has also availability to use decorators that act as event handlers. These decorators are:
* `on_boxer_start` - called before boxer actually runs (arguments: context), Warning, suites are already setup so any change to context will NOT be propagated to derived contexts (suite/test/case)
* `on_boxer_end` - called when boxer is finished (arguments: context, data)
* `on_boxer_setup` - called after setup of boxer (before adding any suite), this is the best place to alter global context.
e.g.:

```python

@export
def restart_service(context):
    """
    some custom code used in all suites, this will be exported since it's decorated by @export
    """

@on_boxer_end
def custom_report(context, data):
    """
    Generate custom data set
    """
    errors = 0
    
    for suite in data['suites']:
        for test in suite['tests']:
            for case in test['cases']:
                if case['errors']:
                    errors += 1

    print('Found {} errors'.format(errors))

@on_boxer_setup
def custom_report(context):
    import requests
    context['session'] = requests.Session()


if __name__ == "__main__":
    if context.get("test_type", None) is None:
        raise ImproperlyConfigured("Please provide test_type.")
```

So we have done couple of things in this example
* we defined `restart_service` function which will be injected into every `__python__` block
* we have set event listener `@on_boxer_end` which will be called after run of boxer.
* we check `test_type` context variable on the start of boxer, and if not given we stop execution (raise `ImproperlyConfigured`)

  
# Suite

Suite has some specific variables that are pop-ed from context and are used to configure suite:

* `name` - suite name is used for output
* `description` - short description what suite does
* `tests` - list of tests, every item can be
    * `string` - filename of test without extension 
    * `structure` - will be passed directly to test setup.
* `before` - block will be run before suite is running (see [Callback blocks](#callback-blocks))
* `after` - block will be run after the suite has been run (see [Callback blocks](#callback-blocks))
* `before_request` - block will be run before every request (see [Callback blocks](#callback-blocks))
* `after_request` - block will be run after every request (see [Callback blocks](#callback-blocks))

Example:

``` yaml
name: "My first test suite"
description: |
    This first testsuite is just an example
    Indentation is automatically dedented
url.query.action: "hello"

before:
    url.query.action: "logged"
    __python__: |
        debug("suite will start to run, I can change data if I want")

tests:
    -
        name: "first test"
        description: "My first test"
        url.endpoint: "version"
        expect:
            response.json.status: 200
    
    # next test will look for file `update_db_test.boxertest` in the same directory as suite
    - update_db_test

    -
        name: "custom except clause test"
        description: "Third test"
        url.endpoint: "/healthcheck"
        expect:
            __python__: |
                assert context['response.json.result.db'] == 200, "Databse check failed."
                assert context['response.json.result.kafka'] == 200, "Kafka check failed."

```


# Test

Test has specific variables used for configuration:

* `name` - test name used for output
* `description` - short description of test
* `datasource` - external datasource (will cover that later in [Datasource](#datasource))
* `cases` - list of cases that will be tested against test data (every case one request will be done) (will cover that later in [Cases](#cases))
* `expect` - dictionary of expect (assert) values, where you can define your expectations from response. (will cover that later in [Expect](#expect))
* `before` - block will be run before test is running (see [Callback blocks](#callback-blocks))
* `after` - block will be run after the test has been run (see [Callback blocks](#callback-blocks))
* `before_request` - block will be run before every request (see [Callback blocks](#callback-blocks))
* `after_request` - block will be run after every request (see [Callback blocks](#callback-blocks))

Example:

```yaml
name: "Some specific test"
url.query.action: "random"
url.query.refresh: true
request.method: "post"
expect:
    response.json.status.__in__: [200, 201, 204]
    __python__: |
        assert context['response.json.status'] % 100 == 3, "Bad status"
        assert context['response.json.status'] % 100 == 4, "Bad status again"
        assert context['response.json.status'] % 100 == 5, "Contact backend engineers ASAP!"
datasource:
    filename: "test.xlsx"
    sheet_name: "first_sheet"
cases:
    -
        url.endpoint: "version"
        expect:
            response.json.status.__in__: [300, 301]
```

# Datasource

Datasource is a feature that will give you possibility to define test data in external sources. 
All these datasources have common configuration `filename`, and every format has also some specific configuration which
I'll describe. Datasources are chosen by filename extension so please be careful how you name your datasource files. 
Warning! datasource block is available only on `test` level not on `suite` level.

Available datasource formats are
* `json` - json data definition
* `yaml` - yaml format definition
* `xlsx` - Excel 2010 format
* `xls` - Old excel format
* `csv` - csv format

Common configuration:
* `filename` - filename of external datasource
* `ignore_value` - value that will be ignored (will not appear in data)
* `none_value` - value that will be treat as `None`

### XLSX Datasource
This datasource can read test data from Excel 2010 file format(xlsx). Every sheet there can be only single data source!!

Example:

```yaml
[datasource]
    filename: "test.xlsx"
    sheet_name: "first_sheet"
```

Configuration:
* sheet_name - name of the sheet where test data is located
* sheet_index - sheet index in workbook (warning it's numbered from 0)

### XLS Datasource
This datasource can read test data from Excel file format(xls). Every sheet there can be only single data source!!

Example:

```yaml
[datasource]
    filename: "test.xls"
    sheet_name: "first_sheet"
```

Configuration:
* sheet_name - name of the sheet where test data is located
* sheet_index - sheet index in workbook (warning it's numbered from 0)

### CSV Datasource
This datasource can read csv files

Example:

```yaml
[datasource]
    filename: "test.csv"
```

### YAML Datasource
This datasource can read yaml files

Example:

```yaml
[datasource]
    filename: "test.yaml"
```

### JSON Datasource
This datasource can read json files

Example:

```yaml
[datasource]
    filename: "test.json"
```

# Cases

Cases are small extension to tests. If no cases are provided, only one request will be done for each test, multiplied by 
data items. So if you set expansion such as `boxer run --context cpe_mac aabbccddeeff --context cpe_mac ffeeddccbbaa`,
test will run 2 requests.
But if you provide multiple cases, every data item will be run through every case and request will be run. This bring
us ability to run more complicated tests, or set of tests where we can define a set of tests for every test item.

In case you have access to case context `context` but if you want to provide data to next case it's isolated. How to
solve this problem? You have access to parent context `parent_context` in before/after callback blocks.
You can imagine it by example (not actual configuration just pseudocode):

Test
* _Case 1_ - insert data
* _Case 2_ - verify if inserted
* _Case 3_ - delete data
* _Case 4_ - verify it's really deleted.


Configuration:
Cases can provide additional expect clause and also they inherit test expect clauses. All other data are left in the context.
That means that you can alter context in every case. Isn't that awesome?
* `expect` - expect dictionary (covered later in [Expect](#expect))
* `before` - block will be run before case (see [Callback blocks](#callback-blocks))
* `after` - block will be run after case has been run(see [Callback blocks](#callback-blocks))

# Expect

Expect is the main part of boxer framework. You can imagine it as set of assertions that are checked after rest request is
called.
It's basically a dictionary of key/values where you can test for return values. It supports wide range of operators,
which are defined as last part of the name.
Well that's a lot of theory, I'll show you some examples:

```yaml
[expect]
    response.json.status: 200
    response.result.name.__eq__: "Peter Vrba"
```

So boxer will test whether `response.json.status` equals to 200 (no operator has been given so `__eq__` is used).
So boxer will test whether `response.result.name` equals to "Peter Vrba".

Expect clauses can do more that just test for equality, here is a list of supported operators:

* `__eq__` - equals to
* `__neq__` - not equals to
* `__gt__` - greater than
* `__gte__` -  greater than or equal
* `__lt__` - lower thatn
* `__lte__` - lower than or equal
* `__in__` - in clause 
* `__nin__` - not in clause
* `__isnone__` - is nont

So let us show them in action:

```yaml
[expect]

    # status is 200
    response.json.status.__eq__: 200 
    # or
    response.json.status: 200 
    
    # status is not 500
    response.json.status.__neq__: 500 
    
    # age is greater than 21
    response.json.user.age.__gt__: 21
    
    # age is greater or equal than 21
    response.json.user.age.__gte__: 21
    
    # age is lower than 21
    response.json.user.age.__lt__: 21
    
    # age is lower or equal than 21
    response.json.user.age.__lte__: 21
    
    # status is one of 200, 201, 204
    response.json.status.__in__: [200, 201, 204]
    
    # status is not one of 404, 405, 500
    response.json.status.__nin__: [404, 405, 500]
    
    # user age is not defined (is None)
    response.json.user.age.__isnone__: True
    
    # user age is defined (is not None)
    response.json.user.age.__isnone__: False
```

So you can see that expect clause are really powerful to do assertions. And that's not the end.
Expect clause supports one really powerfull key which is `__python__`
In this expect you can directly write python code that does some custom assertions or raise custom exceptions. 
Be aware that if you make assertions
you need to provide message, otherwise boxer cannot tell what happened.
Boxer also injects following symbols into `__python__` expect:
* context - whole context that you can use for your custom assertions
* debug - debug function that will print your statements to stdout during writing tests (string format is used)
    debug(format, *args, **kwargs), Warning new format is used so as placeholders use `{}`
    e.g. `debug("This is response {}", context['response.json'])
* logger - boxer logger.

Example:

```yaml
[expect]
    __python__: |
        assert context['response.json.status'] % 100 == 3, "Bad status"
        assert context['response.json.status'] % 100 == 4, "Bad status again"
        assert context['response.json.status'] % 100 == 5, "Are you serious??"
```

Well I can say from my point of view that this should be good enough for all types of assertions (expectations).

# Callback blocks
Suite and tests have special blocks that are evaluated before and after some event. 
These blocks are key values that are passed to request. Also if key is `__python__`, value will be evaluated as python code.

Example:
```yaml
[before_request]
    url.query.refresh: true
    __python__: |
        context['request.headers.AUTH_TOKEN'] = 'token'
```

Available blocks
* Suite - 
    * `before` - before suite is run
    * `after` - after suite is run
    * `before_request` - before every request
    * `after_requeset` - after request is done
* Test -
    * `before` - before test is run
    * `after` - after test is run
    * `before_request` - before every request
    * `after_requeset` - after request is done


Callback blocks have injected various functions (shorthands) and exceptions that can be used for advance control of 
boxer tests.
This list will be expanded by the requests from users of boxer.

Currently you can use these:
* `logger` - python logging logger, this can be used to emit logging messages to log file and/or stdout
* `sleep` - shorthand for pythons `time.sleep`
* `debug_func` - decorator for functions that prints debug information about function call
* `template_func` - decorator that marks function as template function for generating report
* `export` - decorator that marks function/class as exported for all `__python__` blocks (Available only in `boxerconfig.python_locals`) 
* `ImproperlyConfigured` - if this exception is raised, boxer will immediately stop with given message
    e.g.: `raise ImproperlyConfigured("missing cpe")`
* `SkipCase` - current case will be skipped, directly following to next case 
    (available in `before`, `after`, `before_request`, `after_request`)
* `RetryCase` - current case will be retried.
    (available in `before`, `after`, `before_request`, `after_request`)
* `SkipSuite` - if raised suite will be skiped (Only available in `suite.before` callback block)
* `RetrySuite` - if raised suite will be retried (Only available in `expect` callback block), on context `retries_suite`
    will be incremented.

# Command Line

Boxer is shipped as command line application `boxer`. 
For complete help you can try 

    boxer --help 


for complete command documentation please refer to

    boxer <command> --help


Boxer has following available commands:

* `version` - print boxer version
* `info` - print boxer information
* `run` - main command to run boxer suites
* `generate_report` - generate report with given data (obtained by running `boxer run`)

# Installation

Currently boxer is under heavy development, so if you want to test it please run 

    python setup.py develop

When boxer will be stable enough the installation will become

    python setup.py install

# Development

To run the all tests run::

    ./test.sh

### Development
Since boxer is still work in progress, there are couple of [tasks](issues) that needs to be resolved.
I am actively developing (fixing issues) so please read the list before posting new issue.

# Example
Short example could be found [here](examples/). Most of boxer features should be shown in example, there is still some 
work to be done.

You can run this example by navigating into example directory and run:

    boxer --config config.boxerconfig run --context cpe_mac.__choices__ '["aabbccddeeff", "ffeeddccbba"]' suite

or if you want to leave selection of suites to autodiscovery

    boxer --config config.boxerconfig run --context cpe_mac.__choices__ '["aabbccddeeff", "ffeeddccbba"]'

# Author
Peter Vrba <Peter_Vrba@cable.comcast.com>
