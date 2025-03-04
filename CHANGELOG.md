## v1.1.0 (2025-03-04)


- refactor: switch to pyproject.toml for configuration
- change: drop python 3.8 support
- ci: upgrade actions, add python 3.13 to build matrix
- fix: workaround for wasmtime crash on macos
- https://github.com/igrr/astyle_py/issues/7
- change: upgrade wasmtime to 30.0.0
- change(ci): add a job with python 3.12

## v1.0.5 (2023-10-27)


- release v1.0.5
- fix(deps): update pyyaml to 6.0.1
- Fixes incompatibility with Cython 3.0.0

## v1.0.4 (2023-10-03)


- release v1.0.4
- fix(deps): allow newer compatible versions of dependencies
- fix(pre-commit): remove unnecessary 'pass_filenames: true'
- pass_filenames==true by default.

## v1.0.3 (2023-09-27)


- release v1.0.3
- fix(main): fix incorrect warning, cover main with tests

## v1.0.2 (2023-09-26)


- release v1.0.2
- feat: print a note if no files were checked

## v1.0.1 (2023-09-25)


- release v1.0.1
- fix(astyle): fix error handling to not segfault
- fix(rules): remove version option in rules file, since it doesn't work

## v1.0.0 (2023-09-25)


- release v1.0.0
- chore(readme): add badges
- chore(ci): update checkout and setup-python actions
- fix(setup): fix package_data for the new location of WASM files
- feat(deps): update to wasmtime 12.0.0, drop python 3.7
- fix(readme): correct --astyle-version argument syntax
- feat: add support for multiple astyle versions; add 3.4.7

## v0.9.1 (2023-04-13)


- release v0.9.1
- upgrade pre-commit hooks
- fix args.rules not handled
- iterate_files_rules was implemented in 71eb50fba, but I forgot to
update iterate_files to call it.

## v0.9.0 (2022-08-31)


- release v0.9.0
- upgrade wasmtime to 0.40.0
- add CI workflow
- extend README.md and CONTRIBUTING.md
- add a sample
- update setup.cfg, add pyproject.toml
- - change deprecated license_file to license_files
- add classifiers
- implement processing of rules files
- refactor files iteration
- move tests to pytest
- split astyle_wrappers into multiple files
- upgrade python and wasmtime dependencies
- add pre-commit, drop requirements.txt
- update to wasmtime==0.29.0
- * wasmtime version pinned in setup.cfg and requirements.txt
* changes to support new wasmtime API
* move argument parsing out of 'main' into a separate function
* add a couple simple test cases
- Implement more options, expand readme
- initial version
