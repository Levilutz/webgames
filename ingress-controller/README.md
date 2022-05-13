# ingress-controller

This is just a garden helm module / service deploying the standard [kubernetes/ingress-nginx](https://github.com/kubernetes/ingress-nginx) helm chart, with values files for each relevant env. It's simple purpose is to enable ingress-controller variation across various deployment environments. 

This enforces a single notable deviation from the 'standard' way to manage ingress controllers: there's an instance of ingress-nginx in every deployment environment that wants one, deployed in a namespace alongside the pods it's routing to. Given the cost-saving measure of every-deployment-environment-in-one-cluster, this means there could be any number of ingress-nginx instances running in the same cluster.

This is eased by the fact that only the prod (and stage in future) namespaces should have externally-facing ingress controllers with a LoadBalancer. All the development instances should expose through a ClusterIP service that is port-forwarded to a developer machine for dev-mode. 

Consequently, only ingresses deployed to prod should have external-dns annotations. If external-dns had a scoping mechanism this could be more concretely enforced, but for now it's only soft-enforced by dev ingress controllers not having a LoadBalancer (and hence no externally-facing IP to use in DNS A records).

Additionally, each garden helm module in this whole project should refer to this as a deployment dependency if we want to expose the services of that module to the internet OR port-forward it easier for dev-mode.

The ingress-nginx instances between namespaces shouldn't step on each others' toes, as each is scoped to its own namespace alone.
