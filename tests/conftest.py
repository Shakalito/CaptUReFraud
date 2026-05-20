import pytest

from src.common.spark import create_spark_session


@pytest.fixture(scope="session")
def spark():
    spark_session = create_spark_session("PytestSparkSession")

    yield spark_session

    spark_session.stop()