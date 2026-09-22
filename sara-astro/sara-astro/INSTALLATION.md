# Installation

## Requirements

- Python 3.11 or newer
- Internet access for online-mode features (SIMBAD/Gaia queries); not required for offline `Star` calculations

## From PyPI (once published)

```bash
pip install sara-astro
```

With the optional command-line tool:

```bash
pip install "sara-astro[cli]"
```

## From source (development install)

```bash
git clone https://github.com/Nitishsharma234/sara-astro.git
cd sara-astro
pip install -e ".[dev,cli]"
```

The `-e` (editable) install means changes to the source are picked up
immediately without reinstalling.

## Verifying the install

```bash
python -c "from sara_astro import AstroObject; print(AstroObject('Sirius').info())"
```

If this prints a populated summary for Sirius, the install and network
connectivity to SIMBAD/Gaia are both working.

## Running the test suite

```bash
pytest
```

The test suite mocks all catalog network calls, so it runs fully offline
and should pass even without internet access.
