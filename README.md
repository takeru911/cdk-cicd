## CDKによるcode build/pipelineを利用したCI/CDの実現するやつ

https://dev.classmethod.jp/server-side/serverless/aws-cdk-cicd/
をpython & Githubのリポジトリを利用する実装に変えた。
基本的に上の記事を見ればわかるかと

### run

* 依存ライブラリのinstall

```
$ virtualenv .env
$ source .env/bin/activate
$ pip install -r requirements.txt
```

* cloudformationのstack作成し、deploy

```
$ cdk deploy
```
(事前にcdk bootstrapの必要があるかもしれないです)

build対象のリポジトリは https://github.com/takeru911/cdk-lambda です。
