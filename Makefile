# make all       download the data, run the analysis, build the paper (= ./reproduce.sh all)
# make data      download the public inputs listed in data/sources.csv
# make analysis  run every analysis script in dependency order
# make paper     build paper/nhb/si.pdf and paper/nhb/main.pdf
# Options: make analysis WORKERS=4   make data FROM_LOCAL=/path/to/data/raw [ORCID_LOCAL=/path/to/orcid]
WORKERS ?= 1
FROM_LOCAL ?=
ORCID_LOCAL ?=
LOCAL := $(if $(FROM_LOCAL),--from-local $(FROM_LOCAL)) $(if $(ORCID_LOCAL),--orcid-local $(ORCID_LOCAL))

.PHONY: all data analysis paper check-urls

all:
	WORKERS=$(WORKERS) ./reproduce.sh all $(LOCAL)

data:
	./reproduce.sh data $(LOCAL)

analysis:
	WORKERS=$(WORKERS) ./reproduce.sh analysis

paper:
	./reproduce.sh paper

check-urls:
	$${PYTHON:-python3} scripts/download_data.py --check-urls
