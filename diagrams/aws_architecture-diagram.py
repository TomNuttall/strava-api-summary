from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.ci import GithubActions
from diagrams.aws.compute import Lambda
from diagrams.aws.engagement import SES
from diagrams.aws.integration import Eventbridge
from diagrams.aws.management import Cloudwatch, ParameterStore
from diagrams.aws.security import KMS
from diagrams.aws.general import SDK

with Diagram("", filename="aws_architecture-diagram", outformat="png"):
    github_action = GithubActions("Github Action")
    strava_api = SDK("Strava Api")

    with Cluster("AWS"):
        event = Eventbridge("EventBridge")
        lambda_function = Lambda("Lambda")

        event >> Edge(label="Run schedule once a week") >> lambda_function

        lambda_function >> Edge(
            label="Store / Retrive access token") >> KMS("KMS") >> Edge() << ParameterStore("ParameterStore")
        lambda_function >> Edge(label="Send stats summary") >> SES("SES")
        lambda_function >> Edge(
            label="Logging") >> Cloudwatch("CloudWatch")

        lambda_function >> Edge(
            label="Request access token / athlete data") >> strava_api

    github_action >> Edge(label="Deploys lambda code") >> lambda_function
