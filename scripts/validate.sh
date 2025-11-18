#!/bin/bash

CODE=0

while IFS= read -r -d '' file; do
  if ! pajv -s ../data.schema.yml -d "$file"; then
    CODE=1
  fi
done < <(find ../data -maxdepth 1 -type f \( -name "*.yaml" -o -name "*.yml" \) -print0)

exit $CODE
