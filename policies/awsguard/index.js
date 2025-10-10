const { AwsGuard } = require("@pulumi/awsguard");

// Enforce AWSGuard policies as mandatory by default, but downgrade a few noisy
// rules to advisory level for this project. Include multiple key aliases to
// cover renamed policies across AWSGuard versions.
const advisory = { enforcementLevel: "advisory" };

new AwsGuard({
  all: "mandatory",
  apigatewayEndpointType: advisory,
  apiGatewayEndpointType: advisory,
  apigatewayStageCached: advisory,
  apiGatewayStageCached: advisory,
  apiGatewayStageCachingEnabled: advisory,
  s3BucketLoggingEnabled: advisory,
});
