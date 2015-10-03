[![build status](https://travis-ci.org/MatthiasKauer/tim.png?branch=master)](https://travis-ci.org/MatthiasKauer/tim)
**Note: I'm in the process of adapting the cram tests to tim; this is difficult on Windows and happens only when I feel like booting up my Linux machine. I am using tim daily already however**

# tim in a nutshell
tim provides a command-line interface to record a time log.
The following animation shows the basic commands begin, switch, end.
Data is recorded in json format and can be manually adjusted using any text editor. On my system, vim is assigned for this task.
![tim intro gif](gif/tim_intro.gif)

When calling ```tim hl```, commands are piped to [hledger](http://hledger.org) for aggregation. Hledger must be installed separately which is simple thanks to their single exe binary for Windows and the integration in most Linux package management systems (```sudo apt-get install hledger``` should work, for instance).
![tim hledger eval gif](gif/tim_hledger.gif)

# differences to ti
tim tries to simplify [ti](https://github.com/sharat87/ti) by relying on [hledger](http://hledger.org/) (which must be on your path) for number crunching.

Biggest changes:

* hledger omits tasks that are too short. 4min, rounded up to 0.1 h seems to be the cut-off.
* interrupts are gone because the stack is complex; you can call switch if you want to start work on something else. If you enter finish, nothing is automatically started.
* hl command hands over your data to hledger to perform aggregations. [hledger manual](http://hledger.org/manual.html#timelog)
* I'm not sure which program the test cases belong to. Please let me know, so I can amend them and test accordingly. Answer seems to be [cram](https://pypi.python.org/pypi/cram).
* note is gone. 
* tag is gone (for now)
* edit is deactivated till I figure out what it does

This leaves the following commands intact:

* on
* fin
* log
* status
* help

#Installation
Tim is on PyPI: https://pypi.python.org/pypi/tim-ledger_diary

Install via:
```
pip install tim-ledger_diary
```

#File size considerations
My tim-sheet grows roughly 2KB / day. That's about 700kB / year. Probably less if I don't track weekends.
Writing line by line the way I am doing it now is starting to get slow already however (at 6KB). hledger itself is significantly faster. As soon as this difference bothers me enough I will switch to storing in hledger format directly s.t. the speed will no longer be an issue.

#For developers
###Python environment installation
####Windows
We develop using Anaconda with package manager [conda](http://conda.io/).
You can install all packages in our environment (inspect environment.yml beforehand; expect 2-3 min of linking/downloading, probably more if your conda base installation is still very basic or has vastly different packages than mine) using:
```
conda env create
```
if it already exists you may have to remove it first.

    * Read <name> on top of environment.yml
    * Confirm via ```conda env list```
    * Remove ```conda env remove --name <name>```

If you feel like updating the environment, run ```conda env export -f environment.yml``` and commit it to the repository.

# ti &mdash; A silly simple time tracker

`ti` is a small command line time tracking application. Simple basic usage
looks like this

    $ ti on my-project
    $ ti fin

You can also give it human-readable times.

    $ ti on my-project 30mins ago

`ti` sports many other cool features. Read along to discover.

## Wat?

`ti` is a simple command line time tracker. It has been completely re-written in
python (from being a bash script) and has (almost) complete test coverage. It is
inspired by [timed](http://adeel.github.com/timed), which is a nice project
and you should check out if you don't like `ti`. It also takes inspiration from
the simplicity of [t](http://stevelosh.com/projects/t/).

If a time tracker tool makes me think for more than 3-5 seconds, I lose my line
of thought and forget what I was doing. This is why I created `ti`. With `ti`,
you'll be as fast as you can type, which you should be good with anyway.

The most important part about `ti` is that it
provides just a few commands to manage your time tracking and gets out
of your way. All data is saved in a JSON file (`~/.ti-sheet`, can be changed by
setting `$SHEET_FILE`) for easy access to whatever you need to do. Some ideas,

- Read your json file to generate beautiful html reports.
- Build monthly statistics based on tags or the tasks themselves.
- Read the currently working project and make it show up in your terminal
  prompt. May be even with how long you've been on it. (!!!)

Its *your* data.

Oh and by the way, the source is a fairly small python script, so if you know
python, you may want to skim over it to get a better feel of how it works.

*Note*: If you have used the previous bash version of `ti`, which was horribly
tied up to only work on linux, you might notice the lack of *plugins* in this
python version. I am not really missing them, so I might not add them. If anyone
has any interesting use cases for it, I'm willing to consider.

## Usage

Here's the minimal usage style:

    $ ti on my-project
    Start working on my-project.

    $ ti status
    You have been working on my-project for less than a minute.

    $ ti fin
    So you stopped working on my-project.

`on` and `fin` can take a time (format described further down) at which to apply
the action.

    $ ti on another-project 2 hours ago
    Start working on another-project.

    $ ti s
    You have been working on another-project for about 2 hours.

    $ ti fin 30 minutes ago
    So you stopped working on another-project.

Also illustrating in the previous example is short aliases of all commands,
their first letter. Like, `s` for `status`, `o` for `on`, `f` for `fin`, etc.

Put brief notes on what you've been doing.

    $ ti note waiting for Napoleon to take over the world
    $ ti n another simple note for demo purposes

Tag your activities for fun and profit.

    $ ti tag imp

Get a log of all activities with the `log` (or `l`) command.

    $ ti log

## Command reference

Run `ti -h` (or `--help` or `help` or just `h`) to get a short command summary
of commands.

### on

- Short: `o`
- Syntax: `ti (o|on) <name> [<time>...]`

Start tracking time for the project/activity given by `<name>`. For example,

    ti on conquest

tells `ti` to start tracking for the activitiy `conquest` *now*. You can
optionally specify a relative time in the past like so,

    ti on conquest 10mins ago

The format of the time is detailed further below.

### fin

- Short: `f`
- Syntax: `ti (f|fin) [<time>...]`

End tracking for the current activity *now*. Just like with `on` command above,
you can give an optional time to the past. Example

    ti fin 10mins ago

tells `ti` that you finished working on the current activity at, well, 10
minutes ago.

### status

- Short: `s`
- Syntax: `ti (s|status)`

Gives short human readable message on the current status. i.e., whether anything
is being tracked currently or not. Example,

    $ ti on conqering-the-world
    Start working on conqering-the-world.
    $ ti status
    You have been working on `conqering-the-world` for less than a minute.

### tag

- Short: `t`
- Syntax: `ti (t|tag) <tag>...`

This command adds the given tags to the current activity. Tags are not currently
used within the `ti` time tracker, but they will be saved in the json data file.
You may use them for whatever purposes you like.

For example, if you have a script to generate a html report from your `ti` data,
you could tag some activities with a tag like `red` or `important` so that, that
activity will appear in red in the final html report.

Use it like,

    ti tag red for-joe

adds the tags `red` and `for-joe` to the current activitiy. You can specify any
number of tags.

Tags are currently for your purpose. Use them as you see fit.

### note

- Short: `n`
- Syntax: `ti (n|note) <note-text>...`

This command adds a note on the current activity. Again, like tags, this has no
significance with the time tracking aspect of `ti`. This is for your own
recording purposes and for the scripts your write to process your `ti` data.

Use it like,

    ti note Discuss this with the other team.

adds the note `Discuss this with the other team.` to the current activity.

### log

- Short: `l`
- Syntax: `ti (l|log) [today]`

Gives a table like representation of all activities and total time spent on each
of them.

## Time format

Currently only the following are recognized. If there is something that is not
handled, but should be, please open an issue about it or a pull request
(function in question is `parse_time`)

- *n* seconds ago can be written as:
    - *n*seconds ago
    - *n*second ago
    - *n*secs ago
    - *n*sec ago
    - *n*s ago
    - `a` in place of *n* in all above cases, to mean 1 second.
    - Eg., `10s ago`, `a sec ago` `25 seconds ago`, `25seconds ago`.

- *n* minutes ago can be written as:
    - *n*minutes ago
    - *n*minute ago
    - *n*mins ago
    - *n*min ago
    - `a` in place of *n* in all above cases, to mean 1 minute.
    - Eg., `5mins ago`, `a minute ago`, `10 minutes ago`.

- *n* hours ago can be written as:
    - *n*hours ago
    - *n*hour ago
    - *n*hrs ago
    - *n*hr ago
    - `a` or `an` in place of *n* in all above cases, to mean 1 hour.
    - Eg., `an hour ago`, `an hr ago`, `2hrs ago`.

Where *n* is an arbitrary number and any number of spaces between *n* and the
time unit are allowed.

## Status

The project is beta. If you find any bug or have any feedback, please do open an
issue on [Github issues](https://github.com/sharat87/ti/issues).

## Gimme!

You can download `ti` [from the source on
github](https://raw.github.com/sharat87/ti/master/bin/ti)</a>.

- Put it somewhere in your `$PATH` and make sure it has executable permissions.
- Install pyyaml using the command `pip install --user pyyaml`.

After that, `ti` should be working fine.

Also, visit the [project page on github](https://github.com/sharat87/ti) for any
further details.

## Who?

Created and fed by Shrikant Sharat
([@sharat87](https://twitter.com/#!sharat87)). To get in touch, ping me on
twitter or <a href=mailto:shrikantsharat.k@gmail.com>email</a>.

## License

[MIT License](http://mitl.sharats.me).
