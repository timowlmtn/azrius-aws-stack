STACK_NAME        ?= GeovisionImageUploadStack
TEMPLATE_PATH     = web/app/aws/sns/template.yaml
FUNCTION_DIR      = web/app/aws/sns
BUILD_DIR         = build/sns
ZIP_NAME          = sns_function.zip
ZIP_PATH          = $(BUILD_DIR)/$(ZIP_NAME)
S3_CODE_BUCKET    ?= ${S3_DEPLOYMENT_BUCKET}
S3_CODE_KEY       = $(ZIP_NAME)

.PHONY: all package upload deploy clean

all: deploy

package:
	@echo "Packaging SNS Lambda function into $(ZIP_PATH)…"
	@mkdir -p $(BUILD_DIR)
	@zip -j $(ZIP_PATH) $(FUNCTION_DIR)/lambda_function.py

upload: package
	@echo "Uploading $(ZIP_PATH) to s3://$(S3_CODE_BUCKET)/$(S3_CODE_KEY)…"
	@aws s3 cp $(ZIP_PATH) s3://$(S3_CODE_BUCKET)/$(S3_CODE_KEY)

deploy: upload
	@echo "Deploying CloudFormation stack '$(STACK_NAME)'…"
	@aws cloudformation deploy \
		--template-file $(TEMPLATE_PATH) \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_NAMED_IAM \
		--parameter-overrides \
			CodeS3Bucket="$(S3_CODE_BUCKET)" \
			CodeS3Key="$(S3_CODE_KEY)"
	@echo "Deployment complete."

clean:
	@echo "Removing build artifacts…"
	@rm -rf $(BUILD_DIR)

test:
	aws s3 cp data/joan_didion_corvette.jpeg s3://azri.us-data/geovision/test-upload/