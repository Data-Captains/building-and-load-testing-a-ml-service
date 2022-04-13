import { Duration, Stack, StackProps } from "aws-cdk-lib";
import {
  PredefinedMetric,
  ScalableTarget,
  ServiceNamespace,
  TargetTrackingScalingPolicy,
} from "aws-cdk-lib/aws-applicationautoscaling";
import { DockerImageAsset } from "aws-cdk-lib/aws-ecr-assets";
import { ManagedPolicy, Role, ServicePrincipal } from "aws-cdk-lib/aws-iam";
import {
  CfnEndpoint,
  CfnEndpointConfig,
  CfnModel,
} from "aws-cdk-lib/aws-sagemaker";
import { Construct } from "constructs";
import stackOptions from "./options.json";

const autoscalingOptions = stackOptions.autoScaling;
const endpointOptions = stackOptions.sageMaker.endpoint;
const endpointConfigurationOptions =
  stackOptions.sageMaker.endpointConfiguration;
const scalableTargetOptions = autoscalingOptions.scalableTarget;
const targetTrakingScalingPolicyOptions =
  autoscalingOptions.targetTrakingScalingPolicy;

export class CdkMlStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const sageMakerServicePrincipal = new ServicePrincipal(
      "sagemaker.amazonaws.com"
    );

    const sageMakerRole = new Role(this, "SageMakerRole", {
      assumedBy: sageMakerServicePrincipal,
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName("AmazonSageMakerFullAccess"),
      ],
    });

    const sageMakerDockerImage = new DockerImageAsset(
      this,
      "SageMakerDockerImageAsset",
      {
        directory: "lib/docker",
      }
    );

    const sageMakerModel = new CfnModel(this, "SageMakerModel", {
      executionRoleArn: sageMakerRole.roleArn,
      primaryContainer: { image: sageMakerDockerImage.imageUri },
    });

    const sageMakerEndpointConfig = new CfnEndpointConfig(
      this,
      "SageMakerEndpointConfig",
      {
        productionVariants: [
          {
            initialInstanceCount:
              endpointConfigurationOptions.initialInstanceCount,
            initialVariantWeight:
              endpointConfigurationOptions.initialVariantWeight,
            instanceType: endpointConfigurationOptions.instanceType,
            modelName: sageMakerModel.attrModelName,
            variantName: endpointConfigurationOptions.variantName,
          },
        ],
      }
    );

    new CfnEndpoint(this, "SageMakerEndpoint", {
      endpointConfigName: sageMakerEndpointConfig.attrEndpointConfigName,
      endpointName: endpointOptions.endpointName,
    });

    if (autoscalingOptions.useAutoScaling) {
      /**
       * See e.g. https://aws.amazon.com/blogs/machine-learning/configuring-autoscaling-inference-endpoints-in-amazon-sagemaker/
       */
      const resourceId = `endpoint/${endpointOptions.endpointName}/variant/${endpointConfigurationOptions.variantName}`;
      const sageMakerScalableTarget = new ScalableTarget(
        this,
        "SageMakerScalableTarget",
        {
          minCapacity: scalableTargetOptions.minCapacity,
          maxCapacity: scalableTargetOptions.maxCapacity,
          resourceId: resourceId,
          scalableDimension: scalableTargetOptions.scalableDimension,
          serviceNamespace: ServiceNamespace.SAGEMAKER,
        }
      );

      new TargetTrackingScalingPolicy(
        this,
        "SageMakerTargetTrakingScalingPolicy",
        {
          policyName: targetTrakingScalingPolicyOptions.policyName,
          predefinedMetric:
            PredefinedMetric.SAGEMAKER_VARIANT_INVOCATIONS_PER_INSTANCE,
          scaleInCooldown: Duration.seconds(
            targetTrakingScalingPolicyOptions.scaleInCooldown
          ),
          scaleOutCooldown: Duration.seconds(
            targetTrakingScalingPolicyOptions.scaleOutCooldown
          ),
          scalingTarget: sageMakerScalableTarget,
          targetValue: targetTrakingScalingPolicyOptions.targetValue,
        }
      );
    }
  }
}
