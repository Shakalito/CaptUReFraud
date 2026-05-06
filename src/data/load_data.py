from pyspark.sql import SparkSession

def create_spark():
    return SparkSession.builder \
        .appName("FraudDetection") \
        .master("local[*]") \
        .getOrCreate()

def load_data(spark):
    return spark.read.csv("data/raw/*.csv", header=True, inferSchema=True)

def main():
    spark = create_spark()

    df = load_data(spark)

    print("=== SCHEMA ===")
    df.printSchema()

    print("=== SAMPLE ===")
    df.show(5)

    spark.stop()

if __name__ == "__main__":
    main()