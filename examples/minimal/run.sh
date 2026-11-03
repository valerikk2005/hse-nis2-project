docker compose down --volumes &&
docker compose up -d &&
python3 ../../examples/minimal/main.py &&
docker compose down --volumes
