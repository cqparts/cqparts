# `cqparts`

Parts collection for model creation with `cadquery`, and a basis for other parts libraries.

> `=========== UNDER CONSTRUCTION ===========`
>
> As I write this, the `qcparts` is purely a concept.
>
> `cadquery` may have fundamental changes to it's API which will define how this library is designed... therefore design of this library may be done in parallel with `cadquery` updates.
>
> so long story short:
> - _under development_, and
> - _watch this space_

## What is `cqparts`

`cadquery` is a programmatic way of generating CAD models.

`cqparts` is a concept on using `cadquery` in a hierarchy to create complex things with variable scope.

For example, adding a carburettor to a vehicle's chassis should be similar in complexity as adding a nut & bolt to an enclosure.

# Usage

## Built-in Parts

`cqparts` has a few built-in low level components you can add to your creations, and is expected to grow.

- nuts
- bolts
- gears
- bearings
- rods
- motors

just a few of each, it's not intended to be a complete list, beause you can add your own by registering parts.

## Registered Parts

You can make your own parts, and register them with `cqparts` using the `@cadquery_part` decorator. This adds the part to the `cqparts` search list.

```python
import cqparts

@cqparts.cadquery_part
class MyThingy(cqparts.Part):
    pass
    # TODO: design methods?
```

## Creating your own library

as long as each part is registered (with `@cadquery_part` described above) you can create your own library of parts, or import libraries created by others.

```python
import cadquery
import cqparts
import cqparts_mylib
import cqparts_towerpro_servos

from Helpers import show

servo_motor = cqparts.find(
    category='servo',
    make='Tower Pro',
    model='MG90S',
)

show(servo_motor)
```
