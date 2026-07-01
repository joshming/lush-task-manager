#!/bin/bash

DB_NAME="project_management"
DB_USER="lush"
DB_HOST="localhost"
DB_PORT="5432"

USERS=(
  "John|Doe"
  "Jane|Smith"
  "Alice|Johnson"
  "Bob|Brown"
  "Emily|Davis"
)

for user in "${USERS[@]}"; do
  IFS='|' read -r FIRST_NAME LAST_NAME <<< "$user"

  docker exec -i lush_database psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -c "INSERT INTO users (first_name, last_name)
        VALUES ('$FIRST_NAME', '$LAST_NAME');"
done

echo "Done inserting users."