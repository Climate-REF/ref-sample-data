# Changelog

Versions follow [Semantic Versioning](https://semver.org/) (`<major>.<minor>.<patch>`).

Backward incompatible (breaking) changes will only be introduced in major versions
with advance notice in the **Deprecations** section of releases.

<!--
You should *NOT* be adding new changelog entries to this file,
this file is managed by towncrier.
See `changelog/README.md`.

You *may* edit previous changelogs to fix problems like typo corrections or such.
To add a new changelog entry, please see
`changelog/README.md`
and https://pip.pypa.io/en/latest/development/contributing/#news-entries,
noting that we use the `changelog` directory instead of news,
markdown instead of restructured text and use slightly different categories
from the examples given in that link.
-->

<!-- towncrier release notes start -->

## ref-sample-data 0.7.7 (2025-12-15)

### Features

- Added CMIP6 and obs4MIPs data for ESMValTool ozone diagnostics ([#58](https://github.com/CMIP-REF/ref-sample-data/pulls/58))


## ref-sample-data 0.7.6 (2025-10-02)

### Improvements

- Increased the timerange for the ECS diagnostic. ([#54](https://github.com/CMIP-REF/ref-sample-data/pulls/54))


## ref-sample-data 0.7.5 (2025-09-30)

### Features

- Add test data for the OHC-NOAA IOMB diagnostic ([#53](https://github.com/CMIP-REF/ref-sample-data/pulls/53))

### Bug Fixes

- Removes ERA5 ta dataset from obs4REF in preference for obs4MIP ([#354](https://github.com/CMIP-REF/ref-sample-data/pulls/354))


## ref-sample-data 0.7.4 (2025-09-26)

### Improvements

- Removes the ERA5 ta data Obs4REF in preference for fetching from Obs4MIPs directly.
  This also removes the dependency on the climate-ref package. ([#50](https://github.com/CMIP-REF/ref-sample-data/pulls/50))


## ref-sample-data 0.7.3 (2025-09-12)

### Improvements

- Update the cloud scatterplot test data match the period in the ESMValTool recipe. ([#49](https://github.com/CMIP-REF/ref-sample-data/pulls/49))


## ref-sample-data 0.7.2 (2025-09-04)

### Features

- Added data for ESMValTool fire diagnostics. ([#48](https://github.com/CMIP-REF/ref-sample-data/pulls/48))


## ref-sample-data 0.7.1 (2025-08-27)

### Features

- Updated cloud radiative effects diagnostic data. ([#47](https://github.com/CMIP-REF/ref-sample-data/pulls/47))


## ref-sample-data 0.7.0 (2025-08-26)

### Features

- Added the `--only` option to the fetch script to allow regenerating a specific set of requests. ([#42](https://github.com/CMIP-REF/ref-sample-data/pulls/42))
- Added sample data for cloud scatterplots and made some improvements to facilitate that:
  - remove broken code from obs4MIPs data request
  - only download data within requested time range
  - change regridding so it does not crash on parametric vertical coordinates
  - show intake-esgf log messages and update version

  ([#44](https://github.com/CMIP-REF/ref-sample-data/pulls/44))
- Added sample data for sea ice sensitivity diagnostic. ([#45](https://github.com/CMIP-REF/ref-sample-data/pulls/45))
- Added sample data for historical changes in climate variables. ([#46](https://github.com/CMIP-REF/ref-sample-data/pulls/46))

### Improvements

- Perform the calculations on a self-hosted node.
  This greatly reduces the time taken to calculate the results. ([#42](https://github.com/CMIP-REF/ref-sample-data/pulls/42))

### Bug Fixes

- Regenerate the sample data ([#43](https://github.com/CMIP-REF/ref-sample-data/pulls/43))


## ref-sample-data 0.6.3 (2025-05-26)

### Features

- Add snc from CESM2 ([#41](https://github.com/CMIP-REF/ref-sample-data/pulls/41))


## ref-sample-data 0.6.1 (2025-05-18)

### Features

- Add burntFractionAll ([#40](https://github.com/CMIP-REF/ref-sample-data/pulls/40))


## ref-sample-data 0.6.0 (2025-05-16)

### Features

- Update the obs4REF archive ([#34](https://github.com/CMIP-REF/ref-sample-data/pulls/34))
- select a longer time span for nbp ([#35](https://github.com/CMIP-REF/ref-sample-data/pulls/35))
- Added sample data for ESMValTool ENSO diagnostics. ([#37](https://github.com/CMIP-REF/ref-sample-data/pulls/37))

## ref-sample-data 0.5.2 (2025-05-09)

### Features

- Add test data for each ILAMB/IOMB metric ([#31](https://github.com/CMIP-REF/ref-sample-data/pulls/31))


## ref-sample-data 0.5.1 (2025-05-07)

### Features

- Added sample data for cloud radiative effects diagnostic. ([#29](https://github.com/CMIP-REF/ref-sample-data/pulls/29))

### Improvements

- Increased the width of the console output to make it easier to diagnose issues. ([#32](https://github.com/CMIP-REF/ref-sample-data/pulls/32))


## ref-sample-data 0.5.0 (2025-04-28)

### Features

- Deduplicate datasets if multiple timespans are specified.
  The superset of the timespans is used to create the output files. ([#28](https://github.com/CMIP-REF/ref-sample-data/pulls/28))


## ref-sample-data 0.4.6 (2025-04-28)

### Features

- Added climate at global warmings levels sample data. ([#27](https://github.com/CMIP-REF/ref-sample-data/pulls/27))


## ref-sample-data 0.4.5 (2025-04-27)

### Features

- Added sample data for sea ice area seasonal cycle and time series metric. ([#26](https://github.com/CMIP-REF/ref-sample-data/pulls/26))


## ref-sample-data 0.4.4 (2025-04-03)

### Features

- Added PSL data for PMP's extratropical modes of variability ([#25](https://github.com/CMIP-REF/ref-sample-data/pulls/25))


## ref-sample-data 0.4.3 (2025-03-29)

### Features

- Add datasets that from pmp which are not yet published on obs4MIPs ([#24](https://github.com/CMIP-REF/ref-sample-data/pulls/24))

### Improvements

- Refactored intake-esgf-based data requests to have a common base class (`ref_sample_data.data_request.base.IntakeESGFDataRequest`) ([#23](https://github.com/CMIP-REF/ref-sample-data/pulls/23))


## ref-sample-data 0.4.2 (2025-03-27)

### Features

- Added data for Zero Emission Commitment metric. ([#21](https://github.com/CMIP-REF/ref-sample-data/pulls/21))
- Added data for Transient Climate Response to Cumulative CO2 Emissions (TCRE) metric. ([#22](https://github.com/CMIP-REF/ref-sample-data/pulls/22))


## ref-sample-data 0.4.1 (2025-03-01)

### Bug Fixes

- Don't wrap back to 360 degrees of longitude ([#19](https://github.com/CMIP-REF/ref-sample-data/pulls/19))


## ref-sample-data 0.4.0 (2025-03-01)

### Features

- Datasets now span the globe with decreased resolution instead of being a subset of the globe with full resolution. ([#18](https://github.com/CMIP-REF/ref-sample-data/pulls/18))

### Trivial/Internal Changes

- [#17](https://github.com/CMIP-REF/ref-sample-data/pulls/17)


## ref-sample-data 0.3.3 (2025-02-27)

### Features

- Add additional data for a PMP metric ([#14](https://github.com/CMIP-REF/ref-sample-data/pulls/14))
- Allow for the fetching of non-decimated datasets ([#16](https://github.com/CMIP-REF/ref-sample-data/pulls/16))


## ref-sample-data 0.3.2 (2025-02-14)

### Features

- Added ILAMB testing data. ([#13](https://github.com/CMIP-REF/ref-sample-data/pulls/13))


## ref-sample-data 0.3.1 (2025-02-04)

### Features

- Added Obs4MIPs sample data to the fetching script. ([#11](https://github.com/CMIP-REF/ref-sample-data/pulls/11))
- Restructured code into classes so that additional sample datasets can be fetched easily in the future. ([#12](https://github.com/CMIP-REF/ref-sample-data/pulls/12))


## ref-sample-data 0.3.0 (2025-01-21)

### Breaking Changes

- Output files now contain a contiguous time dimension for a selected time span.

  The output files are no longer 6monthly samples of the results.
  This was not directly useful for metrics package developers.
  The output file names now contain the start and end date of the dataset
  instead of mimicking the original dataset. ([#5](https://github.com/CMIP-REF/ref-sample-data/pulls/5))

### Features

- Added the files required to run ESMValTool ECS and TCR metrics. ([#4](https://github.com/CMIP-REF/ref-sample-data/pulls/4))
- Added an action to regenerate the sample data in Pull Requests.

  A comment containing `/regenerate` will trigger the action. ([#7](https://github.com/CMIP-REF/ref-sample-data/pulls/7))

### Bug Fixes

- Migrates the source of truth for data generation to the server and documented the regeneration flow ([#8](https://github.com/CMIP-REF/ref-sample-data/pulls/8))


## ref-sample-data 0.2.1 (2025-01-10)

### Bug Fixes

- Fix the missing leading `v` in the version directory name ([#3](https://github.com/CMIP-REF/ref-sample-data/pulls/3))


## ref-sample-data 0.2.0 (2025-01-10)

### Breaking Changes

- Use the dataset version's from ESGF instead of the values in the netCDF files.
  Different files in the same dataset may contain different versions inside their netCDF files. ([#2](https://github.com/CMIP-REF/ref-sample-data/pulls/2))


## ref-sample-data 0.1.1 (2025-01-08)

### Bug Fixes

- Correct the location of the datasets within the repository ([#1](https://github.com/CMIP-REF/ref-sample-data/pulls/1))


## ref-sample-data 0.1.0 (2025-01-08)

Initial release of the CMIP Rapid Evaluation Framework Sample Data.
