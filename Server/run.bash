docker build --build-arg PGID=<your_PGUID> --build-arg PUID=<your_PUID> -t myapp .
docker run -d -e PGID=<your_PGUID> -e PUID=<your_PUID> myapp
