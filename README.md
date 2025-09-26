# galaxy_tools_management_template

## how to convert your instance to use this template

### assumptions:
- for tool installation you are using exclusively the Main Tool Shed at `https://toolshed.g2.bx.psu.edu`, others can be used but that is not part of the basic walk-through
- you have access to the API key of an admin user of the target Galaxy instance

### step-by-step
- create a new repository using the template `https://github.com/martenson/galaxy_tools_management_template`
- make venv `python -m venv .venv && source .venv/bin/activate`
- install requirements.txt `pip install -r requirements.txt`
- create a folder in the repository named the same as your Galaxy's url, for demonstration purposes the template has a folder with my QA instance: `galaxy-qa2.galaxy.cloud.e-infra.cz`
- to obtain the initial list of tools installed on your instance run `get-tool-list --include_tool_panel_id -g "https://galaxy-qa2.galaxy.cloud.e-infra.cz/" --api_key "API_KEY" galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml --get_all_tools`
    - without `--get_all_tools` script ignores tools which are `uninstalled` but not `deleted`
- I got this `qa2.all.yml`:

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

- Using the `split_tool_yaml.py` script run two following python commands to create one `.yml` file and one `.yml.lock` file per section:

```sh
$ python scripts/split_tool_yaml.py -i galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml -o galaxy-qa2.galaxy.cloud.e-infra.cz
$ python scripts/split_tool_yaml.py -i galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml -o galaxy-qa2.galaxy.cloud.e-infra.cz -l
```

- In this demonstration I ended up with these 6 files inside, named after sections ids:

```sh
$ tree galaxy-qa2.galaxy.cloud.e-infra.cz
galaxy-qa2.galaxy.cloud.e-infra.cz
├── fetch_sequences___alignments.yml
├── fetch_sequences___alignments.yml.lock
├── mapping.yml
├── mapping.yml.lock
├── proteomics.yml
├── proteomics.yml.lock
└── qa2.all.yml

1 directory, 7 files
```

- Modify the schema at `galaxy-qa2.galaxy.cloud.e-infra.cz/schema/.schema.yml` and add the new section ids (`fetch_sequences___alignments`, `mapping`, `proteomics`). This will help you ensure section consistency later.

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

- Now we can run a sanity check tool installation. Nothing will be changed.

```sh
$ find galaxy-qa2.galaxy.cloud.e-infra.cz -name '*.yml.lock' | xargs -n 1 -I {} shed-tools install --toolsfile {} --galaxy galaxy-qa2.galaxy.cloud.e-infra.cz --api_key <API_KEY> --skip_install_resolver_dependencies

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



### inspired by

- https://github.com/galaxyproject/usegalaxy-tools
- https://github.com/usegalaxy-eu/usegalaxy-eu-tools/
- https://github.com/Helmholtz-UFZ/ufz-galaxy-tools
- https://github.com/CESNET/galaxy_tools
