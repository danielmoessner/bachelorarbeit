<!--
This file is part of the replication artifact for
difference verification with conditions:
https://gitlab.com/sosy-lab/research/data/difference-data

SPDX-FileCopyrightText: 2020 Dirk Beyer <https://sosy-lab.org>

SPDX-License-Identifier: Apache-2.0
-->

This is a template for the README.md of your replication artifact.
Please consider the [checklist][1] in our wiki for preparing your artifact.

[1]: https://gitlab.com/sosy-lab/admin/chair/-/wikis/Replication-Artifacts

# Reproduction Package for XXX

[![Apache 2.0 License](https://img.shields.io/badge/license-Apache--2-brightgreen.svg?style=flat)](https://www.apache.org/licenses/LICENSE-2.0)

## Authors

...

## Contents

This artifact consists of five parts:
  1. Setup of tool
  2. Introductory example task
  3. Running exemplary benchmark set
  4. Running full benchmark set
  5. Running analysis of experimental data

The artifact also contains all raw data of our experiment runs.
If you only want to reproduce the claims of our paper on that data,
you can go straight to Section 5.

The raw data of our experiment runs are in folder `XXX`.
The used benchmark tasks are in folder `XXX`.
[Alternatively, you can show the whole folder structure of the artifact and explain everything]


## 1. Setup

### Requirements

We provide a docker image/valgrind image/VM with this repository:

For local use on our own system, the artifact has the following requirements:

- python >= 3.6.9
- java 11
- ...

Requirements can be installed with command `XXX`.

The artifact has been tested on Ubuntu 20.04.

### Installation

If any installation beyond the requirements is necessary,
list the necessary command here.
TIP: write a script that performs all installation tasks,
     so that the user only has to run a single command.

### First run

To check that everything works as expected,
run the following command:

(CHANGE this to some simple commands that show that your tools
are working as expected)

`scripts/cpa.sh -predicateAnalysis doc/example.c`

The tool should output the following:

```
EXPECTED OUTPUT OF ABOVE COMMAND
```


## 2. Example task

We will run our approach XXX on an example task to see its benefits and how to use it.

Run, from the command line:

`COMMAND to run example`

This will run the program on task ... with option ...
The file/verdict/interesting data will be created in `output/data.xml`.

The tool should output the following (see section 'Full Logs' for a complete log) :

```
[...]
IMPORTANT OUTPUT THAT SHOWS IT WORKED
[...]
```


## 3. Running exemplary benchmark set

Since running experiments takes a vast amount of time (upper bound: XXX CPU years),
we don't expect this to be the primary use-case of this artifact.
Instead, our own produced data can be found in folder `data-submission` and will be automatically used
by the data analysis as long as no folder `data-raw` exists (see section 'Data Analysis').

In addition, we provide an examplary benchmark set that shows the benefits of our approach.
To run this benchmark set, run the command below.
Running this command will take approximately XXX hours.

```shell
make example-benchmarks
```

(TIP: It is recommended to use a Makefile or some other script that hides the complexity of running multiple benchmark.py)

At the end of its execution, the command should print the following output
(see section 'Full Logs' for a complete log):

```
[...]
IMPORTANT OUTPUT THAT SHOWS IT WORKED
```

ADD Explanation of benchmark results


## 4. Running experiments

If you want to reproduce all our experiments, you require additional hardware resources.
Running experiments requires at least 5 (virtual) CPU cores and 17 GB of memory.
If you want to run experiments in a virtual machine, make sure to adjust the settings accordingly.

Caution: Running all experiments can take up to XX days.

### Executing benchmarks

Run `make all-benchmarks` to run all experiments.

At the end of its execution, the command should print the following output
(see section 'Full Logs' for a complete log):

```
[...]
IMPORTANT OUTPUT THAT SHOWS IT WORKED
```

## 5. Analysis of experimental data

Our own produced data can be found in folder `data-submission` and will be automatically used
by the data analysis as long as no folder `data-raw` exists.

Run `make analysis` to run the data analyses and create the Figures presented in our work.

The command will put all figures and additional data in folder `data-processed`.

At the end of its execution, the command should print the following output
(see section 'Full Logs' for a complete log):

```
[...]
IMPORTANT OUTPUT THAT SHOWS IT WORKED
```

ADD further explanation of what data is produced and how to interpret it.


## Full Logs

This section contains the full log output for each of the commands named above.
This way, you can make sure that commands worked as expected.

- command 1
```
FULL LOG
```
- ...

## License

This artifact is licensed under the Apache 2.0 License with copyright by Dirk Beyer.
