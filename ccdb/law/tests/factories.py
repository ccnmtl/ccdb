import factory
from django.contrib.auth.models import User
from ccdb.law.models import (
    Snapshot, Area, Consequence, Classification,
    Charge, ChargeChildren
)


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user{0}".format(n))


class SnapshotFactory(factory.DjangoModelFactory):
    class Meta:
        model = Snapshot

    label = factory.Sequence(lambda n: "test snapshot {0}".format(n))
    status = "vetted"


class AreaFactory(factory.DjangoModelFactory):
    class Meta:
        model = Area

    label = factory.Sequence(lambda n: "test area {0}".format(n))
    name = "test"
    snapshot = factory.SubFactory(SnapshotFactory)


class ConsequenceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Consequence

    label = factory.Sequence(lambda n: "test consequence {0}".format(n))
    area = factory.SubFactory(AreaFactory)
    name = "test"


class ClassificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Classification

    snapshot = factory.SubFactory(SnapshotFactory)
    label = factory.Sequence(lambda n: "test classification {0}".format(n))
    name = "test"


class ChargeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Charge

    label = factory.Sequence(lambda n: "test charge {0}".format(n))
    penal_code = factory.Sequence(lambda n: "127.0.{0}".format(n))
    snapshot = factory.SubFactory(SnapshotFactory)
    name = factory.Sequence(lambda n: "127-0-{0}-test-charge".format(n))
    numeric_penal_code = 127.0
    description = "a description"


class ChargeChildrenFactory(factory.DjangoModelFactory):
    class Meta:
        model = ChargeChildren

    parent = factory.SubFactory(ChargeFactory)
    child = factory.SubFactory(
        ChargeFactory,
        snapshot=factory.SelfAttribute('..parent.snapshot')
    )
