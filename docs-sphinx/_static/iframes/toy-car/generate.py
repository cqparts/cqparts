#!/usr/bin/env python

# Get repository root
from subprocess import check_output
CQPARTS_ROOT = check_output(["git", "rev-parse", "--show-toplevel"]).rstrip('\n')

# Add examples folder to path
import sys
import os
sys.path.append(os.path.join(CQPARTS_ROOT, 'examples'))


# ------------------- Import Module -------------------
# Import example as module
import toy_car


# ------------------- Export / Display -------------------
if __name__ == '__main__':
    # Wheel
    wheel = toy_car.Wheel()
    wheel.exporter('gltf')('wheel.gltf')

    # Axle
    axle = toy_car.Axle()
    axle.exporter('gltf')('axle.gltf')

    # Chassis
    chassis = toy_car.Chassis()
    chassis.exporter('gltf')('chassis.gltf')

    # Wheel Assembly
    wheeled_axle = toy_car.WheeledAxle(right_width=2)
    wheeled_axle.exporter('gltf')('wheel-assembly.gltf')
    print(wheeled_axle.tree_str(name='wheel_assembly'))

    # Car Assembly
    car = toy_car.Car()
    car.exporter('gltf')('car.gltf')
    print(car.tree_str(name='car'))
    car.find('chassis').exporter('gltf')('chassis-altered.gltf')
