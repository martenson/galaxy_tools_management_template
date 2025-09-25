# galaxy_tools_management_template

## how to convert your instance to use this template

### assumptions:
- for tool installation you are using exclusively the Main Tool Shed at `https://toolshed.g2.bx.psu.edu`, others can be used but that is not part of the basic walk-through

### step-by-step
- create a new repository using the template `https://github.com/martenson/galaxy_tools_management_template`
- make venv `python -m venv .venv && source .venv/bin/activate`
- install requirements.txt `pip install -r requirements.txt`
- create a folder in the repository named the same as your Galaxy's url, for demonstration purposes the template has a folder with my QA instance, `galaxy-qa2.galaxy.cloud.e-infra.cz`
- `get-tool-list --include_tool_panel_id -g "https://galaxy-qa2.galaxy.cloud.e-infra.cz/" --api_key "API_KEY" galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml --get_all_tools`
    - without `--get_all_tools` script ignores tools which are `uninstalled` but not `deleted`
- you get this qa2.all.yml

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

Split the file into two files per section using two invocations of the `split_tool_yaml.py` script. One file has minimal information (name, owner, section) and the other (the `.lock` file) has details (exact changeset, tool panel id and toolshed url).


Using the two following python commands to create one `.yml` file and one `.yml.lock` file per section:

```sh
$ python scripts/split_tool_yaml.py -i galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml -o galaxy-qa2.galaxy.cloud.e-infra.cz
$ python scripts/split_tool_yaml.py -i galaxy-qa2.galaxy.cloud.e-infra.cz/qa2.all.yml -o galaxy-qa2.galaxy.cloud.e-infra.cz -l
```

In this example I ended up with these 6 files inside, named after sections ids:
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

Modify the schema at `galaxy-qa2.galaxy.cloud.e-infra.cz/schema/.schema.yml` and add the section ids (`fetch_sequences___alignments`, `mapping`, `proteomics`). This will help you ensure section consistency later.

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





### inspired by

- https://github.com/galaxyproject/usegalaxy-tools
- https://github.com/usegalaxy-eu/usegalaxy-eu-tools/
- https://github.com/Helmholtz-UFZ/ufz-galaxy-tools
- https://github.com/CESNET/galaxy_tools
