from __future__ import annotations
from dataclasses import field, dataclass
import random
from datetime import datetime, timedelta
from typing import Type, cast
from faker import Faker
from data.project.base import Dataset, Entity
from uuid import uuid4
from faker_vehicle import VehicleProvider

DATETIME_FORMAT: str = "%Y-%m-%d, %H:%M:%S"


@dataclass
class ParkingDataset(Dataset):
    drivers: list[Driver]
    cars: list[Car]
    garages: list[Garage]
    tickets: list[Tickets]

    @staticmethod
    def entity_types() -> list[Type[Entity]]:
        return [Driver, Car, Garage, Tickets]

    @staticmethod
    def from_sequence(entities: list[list[Entity]]) -> Dataset:
        return ParkingDataset(
            cast(list[Driver], entities[0]),
            cast(list[Car], entities[1]),
            cast(list[Garage], entities[2]),
            cast(list[Tickets], entities[3])
        )

    def entities(self) -> dict[Type[Entity], list[Entity]]:
        res = dict()
        res[Driver] = self.drivers
        res[Car] = self.cars
        res[Garage] = self.garages
        res[Tickets] = self.tickets

        return res

    @staticmethod
    def generate(
            count_of_drivers: int,
            count_of_garages: int,
            count_of_tickets: int) -> ParkingDataset:

        def generate_drivers(number_of_drivers: int, male_ratio: float = 0.5, locale: str = 'hu_HU', unique: bool = False,
                            min_age: int = 0, max_age: int = 100) -> list[Driver]:
            assert number_of_drivers > 0
            assert male_ratio >= 0
            assert male_ratio <= 1

            fake: Faker = Faker()
            drivers: list[Driver] = []

            for counter in range(number_of_drivers):
                generator: Faker = fake if not unique else fake.unique
                male = True if random.random() < male_ratio else False
                drivers.append(
                    Driver(
                        id="P-" + (str(counter).zfill(10)),
                        name=(f'{generator.first_name_male()} {generator.last_name_male()}' if male else
                              f'{generator.first_name_female()} {generator.last_name_female()}'),
                        age=random.randint(min_age, max_age),
                        male=male
                    )
                )

            return drivers

        def generate_cars(drivers: list[Driver], locale: str = "hu_HU", unique: bool = False) -> list[Car]:
            assert len(drivers) > 0

            fake: Faker = Faker(locale)
            fake.add_provider(VehicleProvider)
            cars = []
            for person in drivers:
                generator: Faker = fake if not unique else fake.unique
                cars.append(
                    Car(
                        license_plate=generator.license_plate(),
                        manufacturer=generator.vehicle_make(),
                        model=generator.vehicle_model(),
                        year=generator.vehicle_year(),
                        color=generator.color(),
                        owner_id=person.id,
                    )
                )

            return cars

        def generate_garages(number_of_garages: int, number_of_spots: int = 200, unique: bool = False) -> list[Garage]:
            assert number_of_garages > 0
            assert number_of_spots > 0

            price_of_an_hour = 200 * random.randint(1, 5)

            fake: Faker = Faker()
            garages: list[Garage] = []

            for counter in range(number_of_garages):
                generator: Faker = fake if not unique else fake.unique
                garages.append(
                    Garage(
                        garage_id=str(uuid4()),
                        address=generator.address(),
                        price=price_of_an_hour
                    )
                )

            return garages

        def random_date(start: datetime, end: datetime):
            return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())),)

        def generate_tickets(number_of_tickets: int, cars: list[Car], garages: list[Garage]) -> list[Tickets]:
            assert number_of_tickets > 0
            assert len(cars) > 0
            assert len(garages) > 0

            fake = Faker()

            tickets = []
            for counter in range(number_of_tickets):
                car: Car = random.choice(cars)
                garage: Garage = random.choice(garages)
                date: datetime = random_date(datetime(2019, 1, 1, 0, 0, 0), datetime.now())
                hours: int = random.randint(1, 24)
                tickets.append(
                    Tickets(
                        "TICKET-" + (str(counter).zfill(10)),
                        car.license_plate,
                        garage.garage_id,
                        date.strftime(DATETIME_FORMAT),
                        (date + timedelta(hours=hours)).strftime(DATETIME_FORMAT),
                        garage.price * hours
                    )
                )

            return tickets

        drivers = generate_drivers(number_of_drivers=count_of_drivers, min_age=17, max_age=100, unique=True)
        cars = generate_cars(drivers=drivers)
        garages = generate_garages(number_of_garages=count_of_garages, number_of_spots=random.randint(100, 400),
                                   unique=True)
        tickets = generate_tickets(number_of_tickets=count_of_tickets, cars=cars, garages=garages)
        return ParkingDataset(drivers, cars, garages, tickets)


@dataclass
class Tickets(Entity):
    ticket_id: str = field(hash=True, compare=True)
    license_plate: str = field(repr=True, compare=False)
    garage_id: str = field(repr=True, compare=False)
    from_date: str = field(repr=True, compare=False)
    until_date: str = field(repr=True, compare=False)
    price: int = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Tickets:
        return Tickets(seq[0], seq[1], seq[2], seq[3], seq[4], int(seq[5]))

    def to_sequence(self) -> list[str]:
        return [self.ticket_id, self.license_plate, self.garage_id, self.from_date, self.until_date, str(self.price)]

    @staticmethod
    def field_names() -> list[str]:
        return ["ticket_id", "license_plate", "garage_id", "from_date", "until_date", "price"]

    @staticmethod
    def collection_name() -> str:
        return "tickets"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Tickets.collection_name()} (
            ticket_id VARCHAR(50) NOT NULL PRIMARY KEY,
            garage_id VARCHAR(50),
            from_date VARCHAR(50),
            until_date VARCHAR(50),
            price INTEGER,
            license_plate VARCHAR(50),
            owner_id VARCHAR(50),

            FOREIGN KEY (garage_id) REFERENCES {Garage.collection_name()}(garage_id),
            FOREIGN KEY (owner_id) REFERENCES {Driver.collection_name()}(id),
            FOREIGN KEY (license_plate) REFERENCES {Car.collection_name()}(license_plate)
        );
         """


@dataclass
class Driver(Entity):
    id: str = field(hash=True)
    name: str = field(repr=True, compare=False)
    age: int = field(repr=True, compare=False)
    male: bool = field(default=True, repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Driver:
        return Driver(seq[0], seq[1], int(seq[2]), bool(seq[3]))

    def to_sequence(self) -> list[str]:
        return [self.id, self.name, str(self.age), str(int(self.male))]

    @staticmethod
    def field_names() -> list[str]:
        return ["id", "name", "age", "male"]

    @staticmethod
    def collection_name() -> str:
        return "drivers"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Driver.collection_name()} (
            id VARCHAR(50) NOT NULL PRIMARY KEY,
            name VARCHAR(50),
            age TINYINT,
            male BOOLEAN
        );
        """


@dataclass
class Car(Entity):
    license_plate: str = field(hash=True, compare=True)
    manufacturer: str = field(repr=True, compare=False)
    model: str = field(repr=True, compare=False)
    year: int = field(repr=True, compare=False)
    color: str = field(repr=True, compare=False)
    owner_id: str = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Car:
        return Car(seq[0], seq[1], seq[2], int(seq[3]), seq[4], seq[5])

    def to_sequence(self) -> list[str]:
        return [self.license_plate, self.manufacturer, self.model, str(self.year), self.color, self.owner_id]

    @staticmethod
    def field_names() -> list[str]:
        return ["license_plate", "manufacturer", "model", "year", "color", "owner_id"]

    @staticmethod
    def collection_name() -> str:
        return "car"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Car.collection_name()} (
            license_plate VARCHAR(50) NOT NULL PRIMARY KEY,
            manufacturer VARCHAR(50),
            model VARCHAR(50),
            year INTEGER,
            color VARCHAR(20),
            owner_id VARCHAR(20)
        );
        """


@dataclass
class Garage(Entity):
    garage_id: str = field(hash=True, compare=True)
    address: str = field(repr=True, compare=False)
    price: int = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Garage:
        cars: list[Car] = []
        for car in list(seq[2]):
            cars.append(Car.from_sequence(car))
        return Garage(seq[0], seq[1], int(seq[2]))

    def to_sequence(self) -> list[str]:
        return [self.garage_id, self.address, str(self.price)]

    @staticmethod
    def field_names() -> list[str]:
        return ["garage_id", "address", "price"]

    @staticmethod
    def collection_name() -> str:
        return "garage"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Garage.collection_name()} (
            garage_id VARCHAR(50) NOT NULL PRIMARY KEY,
            address VARCHAR(100),
            price INTEGER
        );
        """
