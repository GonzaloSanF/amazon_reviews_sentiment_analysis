# Calcula top 20 de palabras más frecuentes tras limpieza básica de texto

#!/usr/bin/env python3
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, lower, regexp_replace, col
import sys

def main(input_path, output_path):
    spark = SparkSession.builder.appName("WordFrequency").getOrCreate()
    # Leer CSV sin cabecera y nombrar columnas
    df = spark.read.option("header", False) \
                   .option("sep", ",") \
                   .option("quote", '"') \
                   .option("escape", "\\") \
                   .csv(input_path) \
                   .toDF("label", "title", "text")

    # Limpiar y tokenizar la columna "text"
    words = df.select(
        explode(
            split(
                lower(
                    regexp_replace(col("text"), "[^a-z ]", " ")
                ),
                " +"
            )
        ).alias("word")
    )

    # Filtrar vacíos, agrupar, ordenar y limitar a top 20
    freq = words.filter(col("word") != "") \
                 .groupBy("word") \
                 .count() \
                 .orderBy(col("count").desc()) \
                 .limit(20)

    # Mostrar resultados por consola
    freq.show(truncate=False)

    # Guardar en carpeta results
    freq.coalesce(1) \
        .write \
        .mode("overwrite") \
        .option("header", True) \
        .csv(output_path)

    spark.stop()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: spark-submit word_frequency.py <input.csv> <output_dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
