# Calcula longitud media de reseñas por sentimiento

#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import length, avg, col
import sys

def main(input_path, output_path):
    spark = SparkSession.builder.appName("ReviewLengthStats").getOrCreate()
    # Leer CSV y nombrar columnas
    df = spark.read.option("header", False) \
                   .option("sep", ",") \
                   .option("quote", '"') \
                   .option("escape", "\\") \
                   .csv(input_path) \
                   .toDF("label", "title", "text")

    # Calcular longitud de texto y promedio por sentimiento
    stats = df.withColumn("length", length(col("text"))) \
              .withColumn("sentiment", col("label").cast("int")) \
              .filter(col("sentiment").isin(1, 2)) \
              .groupBy("sentiment") \
              .agg(avg("length").alias("avg_length")) \
              .orderBy("sentiment")

    # Mostrar resultados en consola
    stats.show()

    # Guardar resultados
    stats.coalesce(1) \
         .write \
         .mode("overwrite") \
         .option("header", True) \
         .csv(output_path)

    spark.stop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: spark-submit review_length.py <input.csv> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
