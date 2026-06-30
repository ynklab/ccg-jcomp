# Logical Inference System for Japanese Comparatives
This repository contains code for our paper.

Yosuke Mikami, Daiki Matsuoka, and Hitomi Yanaka.  2025. Implementing a logical inference system for japanese comparatives. In Proceedings of the 5th Natural Logic Meets Machine Learning Workshop.  Association for Computational Linguistics.

## Requirements
* Python 3.7+
* [Vampire](https://vprover.github.io/) 4.9
* [Tsurgeon](https://nlp.stanford.edu/software/tregex.html) 4.2.0

## Setup
Our system uses the scripts available from ccg2lambda.
You need to install **Python** (3.7+), **nltk**, **lxml**, **simplejson**, and **pyyaml**.
If you already have installed python3 and pip, you can install them as follows:
```shell
$ pip install nltk lxml simplejson pyyaml
```
See also installation of ccg2lambda.

The system also uses `pykakasi`, so install it.
```shell
$ pip install pykakasi
```

To run the system, you have to clone this repository first.

* For HTTPS
    ```shell
    $ git clone https://github.com/ynklab/ccg-jcomp.git
    ```
* For SSH
    ```shell
    $ git clone git@github.com:ynklab/ccg-jcomp.git
    ```

## Installation of Vampire and Tsurgeon
* To install Vampire, run the following command:
    ```shell
    $ cd ccg-jcomp
    $ ./tools/install_vampire.sh
    ```
* To install Tsurgeon, run the following command:
    ```shell
    $ cd ccg-jcomp
    $ ./tools/install_tsurgeon.sh
    ```
If `Permission denied` error occurs, change the permission using `chmod` command.

These commands download Vampire 4.9 to `ccg-jcomp/vampire-4.9casc2024` and Tsurgeon 4.2.0 to `ccg-jcomp/stanford-tregex-2020-11-17`, respectively.

The location of each tool is written in `scripts/vampire_dir.txt` and `scripts/tsurgeon_dir.txt`, respectively. You can change the location by editing them.

## Installation of depccg
This system uses depccg as a CCG parser.
```shell
$ pip install cython numpy depccg
```
See also [depccg](https://github.com/masashi-y/depccg).

## Running the system
Let's try the following inference example. The first sentence is a premise which means that Taro is more cheerful than Hanako and presupposes that Hanako is cheerful. The second one is a hypothesis which means that Hanako is cheerful. Thus, the gold answer is *yes* (entailment).

Save this as `ccg-jcomp/test.txt`.
```
太郎は花子以上に明るい。
花子は明るい。
```

You can run the system by the following command.
```shell
$ ./scripts/rte.sh test.txt scripts/semantic_templates_ja_event_degree_multi.yaml
```

The output will be in `results` directory.

### Evaluation on JSeM
```shell
$ ./scripts/eval_jsem.sh <semantic_template>
```
This may take some time.

## Citation
Yosuke Mikami, Daiki Matsuoka, and Hitomi Yanaka.  2025. Implementing a logical inference system for japanese comparatives. In Proceedings of the 5th Natural Logic Meets Machine Learning Workshop.  Association for Computational Linguistics.
```
@inproceedings{Mikami-Matsuoka-Yanaka-2025,
    title = "Implementing a Logical Inference System for Japanese Comparatives",
    author = "Mikami, Yosuke  and
      Matsuoka, Daiki  and
      Yanaka, Hitomi",
    editor = "Abzianidze, Lasha  and
      de Paiva, Valeria",
    booktitle = "Proceedings of the 5th Natural Logic Meets Machine Learning Workshop",
    month = aug,
    year = "2025",
    publisher = "Association for Computational Linguistics"
}
```

## Contact
If you have any questions or feedback, please open an issue.
For private inquiries, please contact ymikami(at)is.s.u-tokyo.ac.jp
