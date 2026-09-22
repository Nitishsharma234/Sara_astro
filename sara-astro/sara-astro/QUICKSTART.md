# Quickstart

## 1. Look up a star by name

```python
from sara_astro import AstroObject

obj = AstroObject("Sirius")

print(obj.identifiers())
print(obj.position())
print(obj.distance())
print(obj.physical_properties())
print(obj.photometry())
print(obj.available_data())
print(obj.info())  # human-readable summary
```

Any of SIMBAD's accepted identifiers work: `"Betelgeuse"`, `"HD 48915"`,
`"HIP 32349"`.

## 2. Understand `DataValue`

Every quantity is a `DataValue`, not a bare number:

```python
dist = obj.distance()

dist.value          # 2.637...
dist.unit           # Unit("pc")
dist.kind           # DataKind.DERIVED
dist.source         # "derived from Gaia DR3 parallax (d = 1000/plx_mas)"
dist.uncertainty    # 0.011...
dist.is_available   # True

dist.to(u.lyr)      # convert to light-years, provenance preserved
```

If a value isn't available, `dist.is_available` is `False` and
`dist.value` is `None` — check `is_available` before using a value in
further math.

## 3. Work offline with a manually specified star

No network call is made in this mode:

```python
from sara_astro import Star

sun = Star(mass=1.0, radius=1.0, temperature=5772.0)

print(sun.surface_gravity())
print(sun.density())
print(sun.escape_velocity())
print(sun.luminosity())
```

If you omit a parameter a calculation needs, you get an `unavailable`
`DataValue` back rather than an exception:

```python
partial = Star(temperature=9900.0)  # no mass or radius
partial.escape_velocity().is_available  # False
```

## 4. Command line

```bash
sara-astro Sirius
sara-astro "HD 189733" --cache
```

## 5. Handling errors

```python
from sara_astro import AstroObject, ObjectNotFoundError, CatalogConnectionError

try:
    obj = AstroObject("definitely not a real star name")
except ObjectNotFoundError:
    print("No catalog match.")
except CatalogConnectionError:
    print("Couldn't reach SIMBAD/Gaia right now.")
```
