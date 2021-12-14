from data.project.model import ParkingDataset
import numpy as np
import matplotlib.pyplot as plt


def number_of_cars_in_garages(dataset: ParkingDataset) -> None:
    garages = [garage.garage_id for garage in dataset.garages]

    values = [0 for _ in garages]

    for ticket in dataset.tickets:
        for garage in dataset.garages:
            if ticket.garage_id == garage:
                values[garages.index(garage.garage_id)] += 1

    fig, ax = plt.subplots()

    ax.bar(garages, values, width=1, edgecolor="white", linewidth=1)
    ax.set_ylabel("number of cars")
    ax.set_title("Number of cars in garages")
    ax.set_xticks(np.arange(len(garages)))
    ax.set_xticklabels(garages)
    ax.legend()

    fig.tight_layout()

    plt.show()


def number_of_cars_by_manufacturer(dataset: ParkingDataset) -> None:

    manufacturers = list(set(car.manufacturer for car in dataset.cars))

    values = [0 for _ in manufacturers]

    for car in dataset.cars:
        for manufacturer in manufacturers:
            if car.manufacturer == manufacturer:
                values[manufacturers.index(manufacturer)] += 1

    fig, ax = plt.subplots()

    ax.bar(manufacturers, values, width=1, edgecolor="white", linewidth=1)
    ax.set_ylabel("number of cars")
    ax.set_title("Number of cars by manufacturer")
    ax.set_xticks(np.arange(len(manufacturers)))
    ax.set_xticklabels(manufacturers)
    ax.legend()

    fig.tight_layout()

    plt.show()


def number_of_drivers_by_age(dataset: ParkingDataset) -> None:

    ages = [i for i in range(1, 120)]

    values = [0 for _ in ages]

    for person in dataset.people:
        for age in ages:
            if person.age == age:
                values[ages.index(age)] += 1

    fig, ax = plt.subplots()

    ax.bar(ages, values, width=1, edgecolor="white", linewidth=1)
    ax.set_ylabel("number of drivers")
    ax.set_title("Number of drivers by age")
    ax.set_xticks(np.arange(len(ages)))
    ax.set_xticklabels(ages)
    ax.legend()

    fig.tight_layout()

    plt.show()
