from aws_cdk import(
     core,
     aws_lambda,
     aws_codebuild as codebuild,
     aws_codepipeline as codepipeline,
     aws_codepipeline_actions as codepipeline_actions,
     aws_iam as iam,
     aws_secretsmanager as secretsmanager
)

owner =  "takeru911"
repo_name = "cdk-lambda"
tag = "my-cicd"
target_function_name = "sample-function"

class MyCicdStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        for stage in ["prd", "dev"] :
            target_function = self.create_function(stage)
            project = self.create_project(target_function, stage)
            source_output = codepipeline.Artifact(self.create_name(stage));
            branch = "master" if stage == "prd" else "develop"
            codepipeline.Pipeline(self, self.create_id("Pipeline", stage),
                                  pipeline_name=self.create_name(stage),
                                  stages=[
                                      codepipeline.StageProps(
                                          stage_name="Source",
                                          actions=[self.create_source_action(branch, source_output)]),
                                      codepipeline.StageProps(
                                          stage_name="Build",
                                          actions=[self.create_build_action(project, source_output)])
                                  ])

    def create_id(self, name, stage):
        return "-".join([tag, name, stage])

    def create_name(self, stage):
        return "_".join([tag, stage])
        
    def create_function(self, stage):
        return aws_lambda.Function(
            self,
            self.create_id("Target", stage),
            function_name=target_function_name + "_" + stage,
            code=aws_lambda.Code.asset("dmy"),
            handler="main.handle",
            runtime=aws_lambda.Runtime.PYTHON_3_6
            )

    def create_project(self, target_function, stage):
        project = codebuild.PipelineProject(
            self,
            self.create_id("Project", stage),
            project_name=self.create_name(stage),
            environment_variables={
                "FUNCTION_NAME": codebuild.BuildEnvironmentVariable(
                    value=target_function.function_name,
                    type=codebuild.BuildEnvironmentVariableType.PLAINTEXT),
                "STAGE": codebuild.BuildEnvironmentVariable(
                    value=stage,
                    type=codebuild.BuildEnvironmentVariableType.PLAINTEXT)
            }
        )
        project.add_to_role_policy(
            iam.PolicyStatement(
                resources=[target_function.function_arn],
                actions=['lambda:UpdateFunctionCode',
                         'lambda:UpdateFunctionConfiguration']
                )
            )
        return project

    def create_source_action(self, branch, source_output):
        secret = secretsmanager.Secret.from_secret_attributes(self,
                                                              branch + "_secret",
                                                              secret_arn="arn:aws:secretsmanager:ap-northeast-1:044768335503:secret:github-api-token-wtevPt")
        oauth_token = secret.secret_value_from_json("github-api-token")

        return codepipeline_actions.GitHubSourceAction(
            action_name="GithubRepo",
            oauth_token=oauth_token,
            output=source_output,
            owner=owner,
            repo=repo_name,
            branch=branch
        )

    def create_build_action(self, project, source_output):
        action_name = "CodeBuild"
        return codepipeline_actions.CodeBuildAction(
            action_name=action_name,
            project=project,
            input=source_output,
            outputs=[codepipeline.Artifact("Test")]
        )

