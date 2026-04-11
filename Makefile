
.PHONY: build-and-publish
build-and-publish:
	rm -rf dist/
	uv build
	uv publish dist/* -u __token__ -p ${PYPI_TOKEN} 


.PHONY: struct
struct:
	tree -I "dist|build|*.egg-info|__pycache__|.venv|tests|*.md" -L 7 > DOCS/STRUCTURE.md
