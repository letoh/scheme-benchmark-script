ifeq ($(origin TMP), undefined)
	TMP = /tmp
endif

CWD      ?= $(PWD)
BENCHDIR ?= bench

ifneq ($(shell test -d $(BENCHDIR); echo -n $$?),0)
$(error the path "$(BENCHDIR)" does not exist, \
	please define BENCHDIR to the correct path)
endif

YPSILON ?= ypsilon
GAUCHE  ?= gosh
GUILE   ?= GUILE_WARN_DEPRECATED=no guile

TOOLS = ypsilon gauche guile
DATA = bench-time.dat bench-ratio.dat

all: bench plot cleanup

%: %.log
	@echo -n

ypsilon.log:
	@-cd $(BENCHDIR); $(YPSILON) --acc=$(TMP) -- run-ypsilon.scm > $(CWD)/$@

gauche.log:
	@-cd $(BENCHDIR); $(GAUCHE) run-gosh.scm > $(CWD)/$@ 2>&1

guile.log:
	@-cd $(BENCHDIR); $(GUILE) run-guile.scm > $(CWD)/$@

bench: $(TOOLS)

$(DATA):
	@./convert.py \
		guile guile.log \
		gosh gauche.log \
		ypsilon ypsilon.log \
		> /dev/null

plot: $(DATA)
	@gnuplot bench.dem

cleanup:
	@rm -f $(DATA)


clean:
	@rm -f $(DATA) *.pdf *.png *.log

