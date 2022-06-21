SHELL:=/bin/bash

deploy-api:
	cd vreapis/ && \
	docker build -f Dockerfile . -t qcdis/vreapi && \
	docker push qcdis/vreapi
	kubectl config use-context kubernetes-admin@kubernetes && \
	kubectl rollout restart deployment vreapi-deployment -n paas

deploy-app:
	cd vre-panel/ && \
	docker build -f Dockerfile . -t qcdis/vreapp && \
	docker push qcdis/vreapp
	kubectl config use-context kubernetes-admin@kubernetes && \
	kubectl rollout restart deployment vreapp-deployment -n paas