for f in $(find "../recreate.git/fase2-descargar/python_api" | grep "\.csv$");do
  # la opcion --no-clobber hace que no se sobreescriba el fichero de destino
	cp --no-clobber $f csv;
done
