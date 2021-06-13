docker_build_with_requirements = '''
FROM docker.io/jupyter/minimal-notebook:latest
COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
$user
'''

docker_build_without_requirements = '''
FROM docker.io/jupyter/minimal-notebook:latest
$user
'''

docker_yaml = '''
version: "3"
services:
  $project_name:
    container_name: $project_name
    build:
      context: ./
      dockerfile: $project_defn
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=$project_token
      - NB_UID=$nb_uid
      - NB_GID=$nb_gid
      - GRANT_SUDO=yes
    volumes:
    - $project_path:/home/jovyan/work:z
    ports:
        - $port:8888
'''

docker_view_yaml = '''
version: "3"
services:
  $project_name:
    container_name: $project_name
    build:
      context: ./
      dockerfile: $project_defn
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=$project_token
    volumes:
    - $project_path:/home/jovyan/work:z
    ports:
        - $port:8888
'''