#!/usr/bin/env python3

from aws_cdk import core

from my_cicd.my_cicd_stack import MyCicdStack


app = core.App()
MyCicdStack(app, "my-cicd")

app.synth()
