const { AwsGuard } = require("@pulumi/awsguard");

// Enforce AWSGuard policies as mandatory by default. Adjust policy levels or
// provide a policy configuration file if you need stack-specific overrides.
new AwsGuard({
  all: "mandatory",
  apigatewayEndpointType: "advisory",
  apigatewayStageCached: "advisory",
  s3BucketLoggingEnabled: "advisory",
});
