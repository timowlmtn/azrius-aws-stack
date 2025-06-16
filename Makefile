default:
	ssh -i ${PEM_KEY} ${EC2_HOST}

DATE := $(shell date +%Y%m%d)
LAYER_SOURCE_DIR=web/app/aws/layer

ls-layers:
	aws s3 ls s3://${S3_DEPLOYMENT_BUCKET}/azrius/

layer-requirements-zip:
	ssh -i ${PEM_KEY} ${EC2_HOST} "rm -rf requirements"
	ssh -i ${PEM_KEY} ${EC2_HOST} "mkdir -p requirements/python/lib/python3.12/site-packages"
	scp -i ${PEM_KEY} $(LAYER_SOURCE_DIR)/requirements.txt ${EC2_HOST}:~/requirements.txt
	ssh -i ${PEM_KEY} ${EC2_HOST} "pip3.12 install --no-cache-dir --ignore-installed --upgrade -r requirements.txt -t requirements/python/lib/python3.12/site-packages"
	ssh -i ${PEM_KEY} ${EC2_HOST} "cd requirements && zip -r requirements.zip ."
	ssh -i ${PEM_KEY} ${EC2_HOST} "aws s3 cp requirements/requirements.zip s3://${S3_DEPLOYMENT_BUCKET}/azrius/${DATE}/requirements.zip"

layer-requirements-build:
	aws cloudformation deploy \
	  --template-file $(LAYER_SOURCE_DIR)/requirements/template.yaml \
	  --stack-name RequirementsLayerStack \
	  --parameter-overrides \
		  S3DeploymentBucket=${S3_DEPLOYMENT_BUCKET} \
		  LayerS3Key=azrius/$(DATE)/requirements.zip \
		  LayerName=requirements-layer \
	  --capabilities CAPABILITY_NAMED_IAM

layer-requirements-clean:
	aws cloudformation --profile ${AWS_PROFILE} delete-stack --region ${AWS_REGION} --stack-name RequirementsLayerStack


layer-requirements-deploy: layer-requirements-build

api-clean:
	aws cloudformation --profile ${AWS_PROFILE} delete-stack --region ${AWS_REGION} --stack-name AzriusCorsApi

api-deploy:
	aws cloudformation deploy \
	  --template-file web/app/aws/api/template.yaml \
	  --stack-name AzriusCorsApi \
	  --parameter-overrides HandlerFunctionArn=$(AWS_LAMBDA_HANDLER_ARN) \
	  --capabilities CAPABILITY_NAMED_IAM

cognito-lambda-test:
	aws lambda invoke \
	  --function-name GoogleFirebaseLambda \
	  --payload '{}' \
	  response.json \
	  --region us-east-1
	cat response.json

cognito-test:
	aws cognito-identity get-id \
	  --region us-east-1 \
	  --identity-pool-id ${REACT_APP_COGNITO_IDENTITY_POOL_ID} \
	  --logins "https://securetoken.google.com/azrius-analytics-cc8a2=${RAW_TOKEN}"

list-bedrock:
	aws bedrock list-foundation-models --region us-east-1

list-bedrock-anthropic:
	aws bedrock list-foundation-models --by-provider anthropic


describe-image:
	python web/app/aws/bedrock/describe_image.py

deploy-vision:
	aws cloudformation deploy \
	  --template-file web/app/aws/lambda/vision/template.yaml \
	  --stack-name AzriusBedrockVision \
	  --parameter-overrides HandlerFunctionArn=$(AWS_LAMBDA_HANDLER_ARN) \
	  --capabilities CAPABILITY_NAMED_IAM

