# webgames

Browser board games, built like an enterprise webapp. Will be available at [games.levilutz.com](https://games.levilutz.com).


## Purpose

To have fun building stuff from the ground up and to keep myself practiced in various industry-relevant technologies.


## Repository Overview

While this repository is a monolith, each directory here is a reasonably independent service / microservice / package. For details, see each directory's `README.md`.

These services should have a few things in common:
* Built to OCI images with either Docker or Buildah
* Deployable to a Kubernetes cluster
* Packaged with Helm
* CI/CD managed with Garden
* For consistency, attaches ingress to `https://<domain>/<game name>` and/or `https://<domain>/api/<game name>`

Besides that, each of these is services is meant to be an independent playground for varying languages, technologies, and design patterns.

Ideally, general and deployment-specific code should be partitioned enough that it's easy to deploy each service on an arbitrary cluster / cloud provider / domain without significant work. Garden has many features which can easily enable movement towards this goal.


## TODO

### More certain plans

* Build out user api for a consistent user experience
* Build chess app with React, REST, Python, PostgresQL stack
* Add a homepage to direct users to various games
    * More full featured? (user profile stuff, centralized leaderboards, idk)


### Things I plan to use here but haven't yet

Backend Languages / Frameworks / Libraries
* FastAPI
* Flask
* Golang
* Python
* Rust
* NodeJs

Frontend Languages / Frameworks / Libraries
* Angular
* Raw JS frontend (maybe a simpler game)
* React
* TypeScript
* Vue

Database technologies
* MongoDB
* MySQL
* PostgresQL

APIs:
* REST (for slower turn-based games)
* GraphQL (for slower complicated games)
* WebSockets (for faster real-time games)
