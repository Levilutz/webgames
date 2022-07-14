# webgames

Browser board games, built like an enterprise webapp. Will be available at [games.levilutz.com](https://games.levilutz.com).


## Purpose

To have fun building stuff from the ground up and to keep myself practiced in various industry-relevant technologies.


## Running

One of the targets of this project is to have as few dependencies as possible. Currently the project's only hard requirement is a modern kubernetes cluster. There are a few softer requirements, listed below in descending order of difficulty to change:
* Sendgrid for email
    * Used by user-api for email verification and password resets. Can be disabled, but those features won't be available. Switching to another email provider would take a moderate amount of work.
* CloudFlare for DNS
    * Currently expected in the external-dns configuration defined in [cluster-init](scripts/cluster-init/setup-external-dns.sh), very little work to adapt.
    * Has some CNAME records to sendgrid domains so they can add SPF records to validate outbound emails. Switching DNS would require going through domain verification and setup through sendgrid again.
* Vultr for hosting the kubernetes cluster
    * PVCs all over set `vultr-block-storage` as their `storageClass`, but this is very simple to adapt for other providers.


## Repository Overview

While this repository is a monolith, each directory here is a reasonably independent service / microservice / package. For details, see each directory's `README.md`.

These services should have a few things in common:
* Built to OCI images with either Docker or Buildah
* Deployable to a Kubernetes cluster
* Packaged with Helm
* CI/CD managed with Garden
* For consistency, attaches ingress to `https://<domain>/<game name>` and/or `https://<domain>/api/<game name>`
    * APIs that don't expose on prod can expose on `https://<domain>/dev/<service name>` in development environments for developer convenience. These ingresses should _definitely_ be disabled in prod environments, and services should never route to these URLs.

Besides that, each of these is services is meant to be an independent playground for varying languages, technologies, and design patterns.

Ideally, general and deployment-specific code should be partitioned enough that it's easy to deploy each service on an arbitrary cluster / cloud provider / domain without significant work. Garden has many features which can easily enable movement towards this goal.


## Technologies in Use

Backend Languages / Frameworks / Libraries
* FastAPI
* Python

Database technologies
* PostgresQL

APIs:
* HTTP (non-RESTful)
* REST

Container / Orchestration / DevOps
* Docker
* Garden
* Helm
* Kubernetes


## TODO

### More certain plans

* Build chess app with React, REST, Python, PostgresQL stack
* Add a homepage to direct users to various games
    * More full featured? (user profile stuff, centralized leaderboards, idk)


### Things I plan to use here but haven't yet

Backend Languages / Frameworks / Libraries
* Flask
* Golang
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

APIs:
* GraphQL (for slower complicated games)
* WebSockets (for faster real-time games)
