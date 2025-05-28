#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import sys

def main(input_file, output_dir):
    spark = SparkSession.builder.appName("Amazon Reviews Sentiment Count").getOrCreate()
    # Leer CSV con inferSchema y manejo de comillas
    df = spark.read.option("header", False) \
                   .option("sep", ",") \
                   .option("quote", '"') \
                   .option("escape", "\\") \
                   .csv(input_file) \
                   .toDF("label", "title", "text")
    # Mapear 1->negative, 2->positive
    mapped = df.withColumn("sentiment",
                           col("label").cast("int")) \
               .filter(col("sentiment").isin(1, 2)) \
               .withColumn("sentiment",
                           (col("sentiment") == 2).cast("string"))  # "true"/"false"

    # Contar
    counts = mapped.groupBy("sentiment").count()

    # Mostrar por consola
    counts.show()

    # Guardar
    counts.coalesce(1).write.csv(output_dir, header=True, mode="overwrite")
    spark.stop()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: spark-submit sentiment_count.py <input.csv> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
