D2 ?= d2
export D2
.PHONY: diagrams check-diagrams lint security test-security check-history

diagrams:
	python3 scripts/diagrams.py render

check-diagrams:
	python3 scripts/diagrams.py check

lint:
	python3 scripts/diagrams.py lint

test-security:
	python3 scripts/test_security.py

security: test-security
	python3 scripts/security.py

check-history:
	python3 scripts/security.py --history
