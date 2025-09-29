# Streamline Galaxy Tool Management

This template is designed to provide Galaxy administrators with a process to ease the burden of maintaining tool repositories installed in a Galaxy instance.

When set up it can also be used as a contact point for users to request tool installations from their admins.

## walkthrough: How To Use This Template

### Assumptions:

The following walkthrough is detailed but makes some assumptions in order to not branch out too much. However the process can be altered to allow for many of these assumptions to change.

- For tool installation you use exclusively the Main Tool Shed at `https://toolshed.g2.bx.psu.edu`
- You have access to the API key of an admin user of the target Galaxy instance in an env variable called `export GALAXY_API_KEY`. You need to run `export GALAXY_API_KEY` to make it available to the Makefile targets.
- You are fine with alphabetical order of tools within the tool sections

### Create Basic Tool Lists
- create a new repository using the template `https://github.com/martenson/galaxy_tools_management_template` and `cd` into the containing folder
- make and activate venv `python3 -m venv .venv && source .venv/bin/activate`
- install requirements.txt `pip install -r requirements.txt`
- create a folder in the repository named the same as your Galaxy's url, for demonstration purposes the template has a folder with my QA instance `galaxy-qa2.galaxy.cloud.e-infra.cz` which this walkthrough will use
- to obtain the initial list of tools installed on your instance run the following [Ephemeris](https://github.com/galaxyproject/ephemeris) command:

```sh
$ get-tool-list --include_tool_panel_id -g "https://galaxy-qa2.galaxy.cloud.e-infra.cz/" --api_key $(GALAXY_API_KEY) -o galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml --get_all_tools
```
(Note without `--get_all_tools` the command ignores tools which are `uninstalled` but not `deleted`).

- This is the `qa2.all.yml` from my Galaxy instance:

```yml
tools:
- name: fastqc
  owner: devteam
  revisions:
  - 5ec9f6bceaee
  tool_panel_section_id: fetch_sequences___alignments
  tool_panel_section_label: Fetch Sequences / Alignments
  tool_shed_url: toolshed.g2.bx.psu.edu
- name: bwa_mem2
  owner: iuc
  revisions:
  - af91699b8d4c
  tool_panel_section_id: mapping
  tool_panel_section_label: Mapping
  tool_shed_url: toolshed.g2.bx.psu.edu
- name: alphafold2
  owner: galaxy-australia
  revisions:
  - c62f678e5555
  tool_panel_section_id: proteomics
  tool_panel_section_label: Proteomics
  tool_shed_url: toolshed.g2.bx.psu.edu
```

- Now for easier management we will split the file into two files per tool panel section. One file has minimal information (name, owner, section) and the other (the `.lock` file) has details (exact changeset, tool panel id and toolshed url).

- We create a new `sections` folder under out instance and using the `split_tool_yaml.py` script run two following python3 commands to create one `.yml` file and one `.yml.lock` file per section:

```sh
$ mkdir galaxy-qa2.galaxy.cloud.e-infra.cz/sections/
$ python3 scripts/split_tool_yaml.py -i galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml -o galaxy-qa2.galaxy.cloud.e-infra.cz/sections/
$ python3 scripts/split_tool_yaml.py -i galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml -o galaxy-qa2.galaxy.cloud.e-infra.cz/sections/ -l
```

- In this demonstration I ended up with these 6 files inside new sections folder, named after sections ids:

```sh
$ tree galaxy-qa2.galaxy.cloud.e-infra.cz/sections/
galaxy-qa2.galaxy.cloud.e-infra.cz/sections/
├── fetch_sequences___alignments.yml
├── fetch_sequences___alignments.yml.lock
├── mapping.yml
├── mapping.yml.lock
├── proteomics.yml
├── proteomics.yml.lock
└── qa2.all.yml

1 directory, 7 files
```

- Now we can run a sanity `make install` check. Nothing should be installed.

```sh
$ INSTANCE=galaxy-qa2.galaxy.cloud.e-infra.cz make install

Storing log file in: /var/folders/pr/tg7jwht95nvcn_f0n8g2zvv00000gn/T/ephemeris_5z6l0zj1
URL should start with http:// or https://. https:// chosen by default.
(1/1) repository fastqc already installed at revision 5ec9f6bceaee. Skipping.
Installed repositories (0): []
Skipped repositories (1): [('fastqc', '5ec9f6bceaee')]
Errored repositories (0): []
All repositories have been installed.
Total run time: 0:00:00.157537
Storing log file in: /var/folders/pr/tg7jwht95nvcn_f0n8g2zvv00000gn/T/ephemeris_i38yh5d1
URL should start with http:// or https://. https:// chosen by default.
(1/1) repository bwa_mem2 already installed at revision af91699b8d4c. Skipping.
Installed repositories (0): []
Skipped repositories (1): [('bwa_mem2', 'af91699b8d4c')]
Errored repositories (0): []
All repositories have been installed.
Total run time: 0:00:00.231629
Storing log file in: /var/folders/pr/tg7jwht95nvcn_f0n8g2zvv00000gn/T/ephemeris_xqaauwnu
URL should start with http:// or https://. https:// chosen by default.
(1/1) repository alphafold2 already installed at revision c62f678e5555. Skipping.
Installed repositories (0): []
Skipped repositories (1): [('alphafold2', 'c62f678e5555')]
Errored repositories (0): []
All repositories have been installed.
Total run time: 0:00:00.141551
```

And that's it, we have basic lists of tools, that are installed on our instance, sorted into files based on their section.

### How to Lint

- Take the schema template called `.schema_temnplate.yml` and copy to `galaxy-qa2.galaxy.cloud.e-infra.cz/schema/.schema.yml`. Then modify it to add the new section ids (`fetch_sequences___alignments`, `mapping`, `proteomics`) of your tools. This will help you ensure section consistency later. It will look like this:

```yml
---
type: map
mapping:
    "tool_panel_section_id":
        type: str
        enum:
              [
                "fetch_sequences___alignments",
                "mapping",
                "proteomics",
              ]
    "tool_panel_section_label":
        type: str

    "tools":
        type: seq
        sequence:
            - type: map
              mapping:
                "name":
                    type: str
                    required: true
                "owner":
                    type: str
                    required: true
                "tool_shed_url":
                    type: str
                    required: false
```

- Run the `lint` using Makefile, supply the INSTANCE url

```sh
$ INSTANCE=galaxy-qa2.galaxy.cloud.e-infra.cz make lint

find ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 16 python3 scripts/yaml_check.py
Checking modified yaml file ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/mapping.yml...
Checking modified yaml file ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml...
Checking modified yaml file ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/proteomics.yml...
find ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 16 -I{} pykwalify -d '{}' -s ./galaxy-qa2.galaxy.cloud.e-infra.cz/schema/.schema.yml
 INFO - validation.valid
 INFO - validation.valid
 INFO - validation.valid
find ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 16 python3 scripts/identify_unpinned.py
```

### Finalize the Tool Lists

If the files failed linting we can use the `fix` Makefile target to fix them.
This process also adds flags for dependency handling. If you want the tool installation process to install dependencies (e.g. the corresponding Conda packages) you can pass `-resdep` to the `fix_lockfile.py` script (maybe add it to the `Makefile`).

```sh
$ INSTANCE=galaxy-qa2.galaxy.cloud.e-infra.cz make fix

# Generate the lockfile or update it if it is missing tools. Also include flags for dependency handling.
find ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 16  python3 scripts/fix_lockfile.py
INFO:root:Processing ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml
INFO:root:Processing ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/proteomics.yml
INFO:root:Processing ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/mapping.yml
# Add the latest revision to every repository that has no revision
find ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 16  python3 scripts/update_tool.py --without --log debug
DEBUG:root:Examining galaxy-australia/alphafold2
DEBUG:root:Examining devteam/fastqc
DEBUG:root:Examining iuc/bwa_mem2
```

In my case the process made the following changes to each lockfile.
Note I don't want the Conda packages installed, because I use singularity images exclusively so I used `-resdep` and therefore got `install_resolver_dependencies: false` in my lockfiles.

```diff
diff --git a/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/mapping.yml.lock b/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/mapping.yml.lock
index 6b2083f..50d5091 100644
--- a/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/mapping.yml.lock
+++ b/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/mapping.yml.lock
@@ -1,3 +1,6 @@
+install_repository_dependencies: true
+install_resolver_dependencies: false
+install_tool_dependencies: false
 tools:
 - name: bwa_mem2
   owner: iuc
@@ -5,4 +8,3 @@ tools:
   - af91699b8d4c
   tool_panel_section_id: mapping
   tool_panel_section_label: Mapping
-  tool_shed_url: toolshed.g2.bx.psu.edu
```

And the resulting lockfile looks like this:

```yml
install_repository_dependencies: true
install_resolver_dependencies: false
install_tool_dependencies: false
tools:
- name: bwa_mem2
  owner: iuc
  revisions:
  - af91699b8d4c
  tool_panel_section_id: mapping
  tool_panel_section_label: Mapping
...
- more tools here
```

### Update a tool

Let's say I want to update tools from the owner `devteam`. I can run the following Makefile target:

```sh
$ REPO_OWNER=devteam INSTANCE=galaxy-qa2.galaxy.cloud.e-infra.cz make update-owner
find ./galaxy-qa2.galaxy.cloud.e-infra.cz/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 16  python3 scripts/update_tool.py --owner devteam
INFO:root:Fetching updates for devteam/fastqc
INFO:root:Found newer revision of devteam/fastqc (2c64fded1286)
```

And it will result in the following change in my `.yml.lock` file. The `fastqc` from `devteam` has a new latest release and its revision has been added.


```diff
--- a/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml.lock
+++ b/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml.lock
@@ -5,6 +5,7 @@ tools:
 - name: fastqc
   owner: devteam
   revisions:
+  - 2c64fded1286
```

Now when I run the `make install` target, the new revision (`2c64fded1286`) will be installed on my instance.

```sh
$ INSTANCE=galaxy-qa2.galaxy.cloud.e-infra.cz make install

Storing log file in: /var/folders/y1/w_qtyhld4mz_7x0ns514twpr0000gn/T/ephemeris_zzjwc456
URL should start with http:// or https://. https:// chosen by default.
(1/1) Installing repository fastqc from devteam to section "None" at revision 2c64fded1286 (TRT: 0:00:00.886010)
	repository fastqc installed successfully (in 0:00:07.420886) at revision 2c64fded1286
Installed repositories (1): [('fastqc', '2c64fded1286')]
...
log continues
```

Note:
 - If you want to update a subset of tools from the owner remove the revisions you don't want.
 - To only update a specific repository run `REPO_NAME=fastqc make update-repo`
 - To update all run `make update-all`
 - You can also run the `scripts/update_tool.py` directly

### Add New Tool

To add new tool modify the `.yml` file of the corresponding section and add the `owner` and the `name`. E.g.:

```diff
--- a/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml
+++ b/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml
@@ -2,3 +2,5 @@ tool_panel_section_label: Fetch Sequences / Alignments
 tools:
 - name: fastqc
   owner: devteam
+- name: fastp
+  owner: iuc
```

Now execute `make fix` to fetch the information about latest revision and add it to the `.yml.lock` file. The resulting entry will look like this.

```diff
--- a/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml.lock
+++ b/galaxy-qa2.galaxy.cloud.e-infra.cz/sections/fetch_sequences___alignments.yml.lock
@@ -5,6 +5,13 @@ tools:
 - name: fastqc
   owner: devteam
   revisions:
   - 2c64fded1286
   - 5ec9f6bceaee
   tool_panel_section_id: fetch_sequences___alignments
   tool_panel_section_label: Fetch Sequences / Alignments
+- name: fastp
+  owner: iuc
+  revisions:
+  - 1c183b0a6cfd
+  tool_panel_section_id: fetch_sequences___alignments
+  tool_panel_section_label: Fetch Sequences / Alignments
```

Your lists are now ready for installation, you can run `make install`.

## Configure GitHub Actions To Lint and Fix

### (optional) Automate Tool Installation using CRON

### (optional) Simplify Your Life With Tool Panel Views

Order of sections and tools is persisted by Galaxy in the `integrated_tool_conf.xml` file.
However what is in this file is affected by the contents and the loading order of **all** tool configuration files.
In addition to that the contents of this integrated configuration is regenerated on Galaxy restart.

These points above make the task of managing the Galaxy's toolset complicated.
However, instead of modifying this file one can opt-in to use tool panel views instead, bypassing these steps.

#### Configure Galaxy to use panel views

```yml
  # Directory to check out for toolbox tool panel views. The path is
  # relative to the Galaxy root dir.  To use an absolute path begin the
  # path with '/'.  This is a comma-separated list.
  panel_views_dir: config/plugins/activities

  # Default tool panel view for the current Galaxy configuration. This
  # should refer to an id of a panel view defined using the panel_views
  # or panel_views_dir configuration options or an EDAM panel view. The
  # default panel view is simply called `default` and refers to the tool
  # panel state defined by the integrated tool panel.
  default_panel_view: all_tools
```

#### Define a Tool Panel View

Take [an example tool panel view](galaxy-qa2.galaxy.cloud.e-infra.cz/plugins/activities/all_tools.yml) in this template.
Modify it for your purposes, store it in `galaxy_dir/config/plugins/activities` and enable using the options above. Restart Galaxy.

Beside the root element (`id: all_tools`) you define the ordered `items:` (section ids from your `.yml.lock` files) and separate section groups by `type: label`.
This will ensure consistent ordering of the sections. All tools within the section are going to be sorted alphabetically, a consistent and predictable approach for the users.

See the minimal excerpt below.

```yml
name: Tools
type: generic
id: all_tools
items:
- sections:
  - upload_file
  - get_data
  - data_source_tools
  - send_data
  - collection_operations
  - expression_tools
- id: general_text_label
  text: General Text Tools
  type: label
- sections:
  - text_manipulation
  - filter_and_sort
```

## todos and ideas

- make this walkthrough a GTN training


## inspired by

- https://github.com/galaxyproject/usegalaxy-tools
- https://github.com/usegalaxy-eu/usegalaxy-eu-tools/
- https://github.com/Helmholtz-UFZ/ufz-galaxy-tools
- https://github.com/CESNET/galaxy_tools

## thanks to

- Nate Coraor
- Helena Rashe
- Matthias Bernt
- Bjoern Gruening
- Marius van den Beek
