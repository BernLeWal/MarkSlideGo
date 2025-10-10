# Contribute MarkSlide Go

## Installation

* Create a [.env](.env) file in the project root. See [.env.sample](.env.sample)
* Install [Node.js](https://nodejs.org/en)  
    The Marp-Tool uses NodeJs > v16 which has to be installed prior to execution of the CLI tool.  
    Set the path to the npx-executable in the [.env](.env) file.
* Install the Marp CLI client
    For a local install use:
    ```shell
    npm install --save-dev @marp-team/marp-cli    
    ```
    Check if it works using:
    ```shell
    npx @marp-team/marp-cli@latest -v
    ```
* Install Google-Chrome (required for the html-rendering)
* Install the [Marp for VS Code](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode) extension
* Activate VS Code-Setting: Markdown > Marp: HTML  
    to support html-based styling and multi-column slides, see [https://github.com/orgs/marp-team/discussions/192#discussioncomment-1517399]
* Install Tesseract  
    Installers see [https://www.baeldung.com/java-ocr-tesseract#setup], Set the path to the tesseract-executable in the [.env](.env) file.
* Download and install better language files from [https://github.com/tesseract-ocr/tessdata/tree/main] (just replace the previously installed .traineddata files)
* Install Python (>3.10), create virtual environment (venv) and activate it
* Install the necessary python libraries
    ```shell
    pip install -r requirements.txt
    ```

## Usage with Docker

### Build and Run on local Docker environment

```shell
docker compose build
docker compose up -d
docker exec -it markslidego bash
```

This opens a shell in the docker container, now you have to clone the courses, e.g. fhtw

```shell
git clone https://git.technikum-wien.at/walliscb-projectspace/kb/courses.git ./courses/fhtw
```

Then run the generation process manually

```shell
python generate_course.py fhtw/bif3_swen1
```

Afterwards you'll find a ZIP file with all the generated artifacts in `/app/courses/fhtw/output/bif3_swen1.zip`.

### Build Docker Image for Docker Hubs

Build the image locally:

```shell
docker build -t markslidego .
docker tag markslidego markslidego:latest
# Verfiy if created
docker images markslidego
```

Publish the image to the hub.docker.com registry:  
Attention: Replace *codepunx* with your own registry username.

```shell
docker tag markslidego:latest codepunx/markslidego:latest

docker login
docker push codepunx/markslidego:latest
```

Run the Docker image via Docker Hub:  
Remarks: No python, NodeJS, etc. .. tools need to be installed locally, just Docker.
```shell
docker run -it --rm codepunx/markslidego /bin/bash
```

This opens a shell in the docker container, now you have to clone the courses

```shell
git clone {{your-remote-repo}} ./courses/{{course-dir}}
```

Then run the generation process manually

```shell
python generate_moodle.py {{course-dir}} [<filter_topic>] [<filter_md_file>]
```

Afterwards you'll find a ZIP file with all the generated artifacts in `/app/courses/{course}/output/`.

