# ─── Variables ──────────────────────────────────────────────────────────────
STACK_NAME     ?= azrius-geoview-stack
TEMPLATE_PATH  ?= web/app/aws/${AZRIUS_APP_FOLDER}/stack/template.yaml
LAMBDA_DIR     ?= web/app/aws/${AZRIUS_APP_FOLDER}
ZIP_NAME       ?= handler.zip
BUILD_DIR      ?= ${AZRIUS_HOME}/build/geoview

# pulled in from your env
S3_BUCKET      ?= $(AZRIUS_APP_BUCKET)
FOLDER_PREFIX  ?= $(AZRIUS_APP_FOLDER)
SNS_TOPIC      ?= $(AZRIUS_APP_SNS)
SQS_QUEUE      ?= $(AZRIUS_APP_SQS)
LAMBDA_NAME    ?= $(AZRIUS_APP_LAMBDA)
PYTHON_RUNTIME ?= $(AZRIUS_APP_PYTHON)
REGION         ?= $(AZRIUS_APP_REGION)

S3_CODE_BUCKET ?= ${S3_DEPLOYMENT_BUCKET}
S3_CODE_KEY = $(ZIP_NAME)

.PHONY: all package deploy teardown clean

all: deploy

ZIP_ZEN_GUIDE=zen_guide_handler.zip

package:
	@echo "→ Packaging all Lambdas..."
	mkdir -p $(BUILD_DIR)

	@echo "→ Packaging main handler..."
	cd $(LAMBDA_DIR)/lambda && zip -j $(BUILD_DIR)/$(ZIP_NAME) handler.py

	@echo "→ Packaging Zen Guide handler..."
	cd $(LAMBDA_DIR)/zen_guide && zip -j $(BUILD_DIR)/$(ZIP_ZEN_GUIDE) handler.py

upload: package
	@echo "Uploading $(BUILD_DIR)/$(ZIP_NAME) to s3://$(S3_CODE_BUCKET)/$(S3_CODE_KEY)..."
	@aws s3 cp $(BUILD_DIR)/$(ZIP_NAME) s3://$(S3_CODE_BUCKET)/$(S3_CODE_KEY)
	@aws s3 cp $(BUILD_DIR)/$(ZIP_ZEN_GUIDE) s3://$(S3_CODE_BUCKET)/$(ZIP_ZEN_GUIDE)


DEPLOY_TS=$(shell date +%s)
VERSION=$(shell git rev-parse --short HEAD)

update: update-azirus update-zen-guide

update-zen-guide: upload
	@echo "→ Updating Zen Guide Lambda code: s3 $(S3_CODE_BUCKET) key $(ZIP_ZEN_GUIDE)'…"
	aws lambda update-function-code \
	  --function-name $(LAMBDA_NAME)-zen-guide \
	  --s3-bucket $(S3_CODE_BUCKET) \
	  --s3-key $(ZIP_ZEN_GUIDE) \
	  --no-cli-pager

update-azrius: upload
	@echo "→ Update $(LAMBDA_NAME) code: s3 $(S3_CODE_BUCKET) key $(S3_CODE_KEY)'…"
	aws lambda update-function-code \
	  --function-name $(LAMBDA_NAME) \
	  --s3-bucket $(S3_CODE_BUCKET) \
	  --s3-key $(S3_CODE_KEY) \
	  --no-cli-pager



deploy: upload
	@echo "→ Deploying CloudFormation stack '$(STACK_NAME)'…"
	aws cloudformation deploy \
		--template-file $(TEMPLATE_PATH) \
		--stack-name $(STACK_NAME) \
		--parameter-overrides \
			AzriusAppBucket=$(S3_BUCKET) \
			AzriusAppFolder=$(FOLDER_PREFIX) \
			BedrockModelArn=${AZRIUS_APP_MODEL_ARN} \
			AzriusAppSns=$(SNS_TOPIC) \
			AzriusAppSqs=$(SQS_QUEUE) \
			AzriusAppLambda=$(LAMBDA_NAME) \
			AzriusAppPython=$(PYTHON_RUNTIME) \
			CodeS3Bucket="$(S3_CODE_BUCKET)" \
			CodeS3Key="$(S3_CODE_KEY)" \
			CodeS3Version=$(VERSION) \
			DeployTimestamp="$(DEPLOY_TS)" \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--region $(REGION)

.PHONY: archive-bucket
archive-bucket:
	@echo "→ Archiving bucket $(AZRIUS_APP_BUCKET) to $(AZRIUS_APP_BUCKET)-archive…"; \
	ARCHIVE_BUCKET="$(AZRIUS_APP_BUCKET)-archive"; \
	# create archive bucket if needed (ignore errors if it already exists) \
	echo "→ Creating archive bucket $$ARCHIVE_BUCKET if it does not exist…"; \
	aws s3 mb s3://$$ARCHIVE_BUCKET --region $(REGION) || true;
	# sync all objects to archive \
	echo "→ Syncing contents of bucket $(AZRIUS_APP_BUCKET) to archive bucket $$ARCHIVE_BUCKET…"; \
	aws s3 sync s3://$(AZRIUS_APP_BUCKET) s3://$$ARCHIVE_BUCKET; \
	# delete source bucket and its contents \
	echo "→ Deleting contents of bucket $(AZRIUS_APP_BUCKET)…"; \
	aws s3 rm s3://$(AZRIUS_APP_BUCKET) --recursive || true;
	echo "→ Deleting bucket $(AZRIUS_APP_BUCKET)…"; \
	aws s3 rb s3://$(AZRIUS_APP_BUCKET) --force || true;


teardown: archive-bucket
	@echo "→ Deleting CloudFormation stack '$(STACK_NAME)'…"
	aws cloudformation delete-stack \
		--stack-name $(STACK_NAME) \
		--region $(REGION)
	@echo "→ Waiting for stack deletion to complete…"
	aws cloudformation wait stack-delete-complete \
		--stack-name $(STACK_NAME) \
		--region $(REGION)

clean:
	@echo "→ Cleaning build artifacts…"
	rm -rf $(BUILD_DIR)

TODAY := $(shell date +%F)

test:
	aws s3 sync data/geovision/test \
	  s3://$(S3_BUCKET)/$(FOLDER_PREFIX)/test/joan_didion/$(TODAY)/34.1033_-118.3512


# web/app/aws/azrius-geovision/Makefile

# -------------------------------------------------------------------
# Use `aws s3 sync` to push the entire local `s3/` directory tree
# up to S3 under geovision/<COGNITO_ID>/. This makes the bucket
# “default data root” mirror your local folder structure.
#
# Usage:
#   cd web/app/aws/azrius-geovision
#   make sync-default-data COGNITO_ID=us-east-1:abcd1234-5678-efgh-90ij-klmnopqrstuv
#
# The local folder `s3/` might contain:
#   s3/
#   ├─ smith_001/
#   │  └─ project.json
#   ├─ another_project/
#   │  └─ project.json
#   └─ ...
#
# After syncing, S3 will contain:
#   s3://azri.us-data/geovision/<COGNITO_ID>/
#       smith_001/project.json
#       another_project/project.json
#       ...
# -------------------------------------------------------------------

# Local root folder containing default data
LOCAL_S3_ROOT := web/app/aws/azrius-geovision/s3

# Must be passed on the CLI:
ifndef COGNITO_ID
$(error You must specify COGNITO_ID, e.g. make sync-default-data COGNITO_ID=us-east-1:abcd1234-5678-efgh-90ij-klmnopqrstuv)
endif

# Remote prefix under which to mirror LOCAL_S3_ROOT
REMOTE_PREFIX := geovision/$(COGNITO_ID)/

.PHONY: all sync-default-data clean-default-data

all: sync-default-data

# ─── Sync local “s3/” tree up to geovision/<COGNITO_ID>/ ───────────────
sync-default-data:
	@echo "→ Syncing local '$(LOCAL_S3_ROOT)/' to 's3://$(BUCKET_NAME)/$(REMOTE_PREFIX)'"
	@if [ ! -d "$(LOCAL_S3_ROOT)" ]; then \
	  echo "❌ Local folder '$(LOCAL_S3_ROOT)' not found."; \
	  exit 1; \
	fi
	@AWS_REGION=$(AWS_REGION) aws s3 sync \
	  --acl private \
	  "$(LOCAL_S3_ROOT)/" \
	  "s3://$(BUCKET_NAME)/$(REMOTE_PREFIX)"
	@echo "✅ Sync complete. S3 contains:"
	@AWS_REGION=$(AWS_REGION) aws s3 ls "s3://$(BUCKET_NAME)/$(REMOTE_PREFIX)" --recursive

# ─── Optional: Remove everything under geovision/<COGNITO_ID>/ ──────────
clean-default-data:
	@echo "→ Removing all objects under 's3://$(BUCKET_NAME)/$(REMOTE_PREFIX)'"
	@AWS_REGION=$(AWS_REGION) aws s3 rm \
	  "s3://$(BUCKET_NAME)/$(REMOTE_PREFIX)" --recursive || echo "⚠️ Nothing to delete."
	@echo "✅ Removal complete."

test-fengshui:
	curl -X POST https://295f55kg2f.execute-api.us-east-1.amazonaws.com/prod/fengshui \
	  -H "Content-Type: application/json" \
	  -d '{ \
	        "folder": "geovision/test/joan_didion/2025-06-17/34.1033_-118.3512" \
	      }'