# galaxy_tools_management_template

This template is designed to provide Galaxy administrators with a process to ease the burden of maintaining tool repositories installed in a Galaxy instance.

When set up it can also be used as a contact point for users to request tool installations.

## Convert your instance to use this template

### assumptions:
- for tool installation you are using exclusively the Main Tool Shed at `https://toolshed.g2.bx.psu.edu`, others can be used but that is not part of the basic walk-through
- you have access to the API key of an admin user of the target Galaxy instance in a variable called `GALAXY_API_KEY`

### step-by-step
- create a new repository using the template `https://github.com/martenson/galaxy_tools_management_template`
- make venv `python3 -m venv .venv && source .venv/bin/activate`
- install requirements.txt `pip install -r requirements.txt`
- create a folder in the repository named the same as your Galaxy's url, for demonstration purposes the template has a folder with my QA instance: `galaxy-qa2.galaxy.cloud.e-infra.cz`
- to obtain the initial list of tools installed on your instance run the following Ephemeris command.

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

- Now we can run a sanity check tool installation. Nothing will be changed.

```sh
$ find galaxy-qa2.galaxy.cloud.e-infra.cz/sections -name '*.yml.lock' | xargs -n 1 -I {} shed-tools install --toolsfile {} --galaxy galaxy-qa2.galaxy.cloud.e-infra.cz --api_key $(GALAXY_API_KEY) --skip_install_resolver_dependencies

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

## Set up linting

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

## Finalize the yml files

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
Note I don't want the Conda packages installed, because I use singularity images exclusively so `install_resolver_dependencies: false` is what I got.

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



### inspired by

- https://github.com/galaxyproject/usegalaxy-tools
- https://github.com/usegalaxy-eu/usegalaxy-eu-tools/
- https://github.com/Helmholtz-UFZ/ufz-galaxy-tools
- https://github.com/CESNET/galaxy_tools
