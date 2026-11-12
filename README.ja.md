# 4D Plugin Example

[English](README.md) | [日本語](README.ja.md)

[`miyako/4d-plugin-example`](https://github.com/miyako/4d-plugin-example) は、
あいさつを返すネイティブ4Dプラグインの実習用リポジトリです。
製品コードと解説はこのリポジトリで管理し、実行用パイプラインは
固定した `plugin-template` サブモジュールから生成します。

## あいさつコマンド

```4d
$greeting:=example_greeting("Miyako"; example_greeting_morning)
// "Good morning Miyako"
$automatic:=example_greeting("宮古")
// 現在のローカル時刻に応じたあいさつ
```

`example_greeting(name {; type}): Text` はText型の名前と、省略可能な
Longint型の種類を受け取ります。Unicode名と空の名前も4Dテストで確認します。

| 定数 | 値 | あいさつ |
|---|---|---|
| `example_greeting_default` | 0 | ローカル時刻：03:00–11:59は朝、12:00–17:59は昼、それ以外は夜 |
| `example_greeting_morning` | 1 | `Good morning ` |
| `example_greeting_afternoon` | 2 | `Good afternoon ` |
| `example_greeting_evening` | 3 | `Good evening ` |

マニフェストがセレクター1をコマンドに対応付け、`constants.xlf` が定数を
定義します。C++実装はプラグイン呼び出しの中だけでSDKを使用します。
これは元の小さな実習用サンプルであり、汎用文字列ライブラリではありません。

## ソースと固定リビジョン

あいさつの実装、マニフェスト、定数、ネイティブIDEプロジェクト、4Dテストは
[`f8e20f0`](https://github.com/miyako/4d-plugin-template/tree/f8e20f052407c3e74c33192884dc82b31a2bd27a/example)
からそのまま引き継いでいます。CMake、バンドルのInfo.plistテンプレート、
ルートの `VERSION` のみ正規のexample overlayを使用します。
ビルドの正規経路はCMakeです。従来のXcode・Visual Studioプロジェクトは
参考資料であり、リリース経路ではありません。

`plugin-template` は公開済みコミット
[`5a9997767fe3f6ba31e0da9ccdd1be74c891168f`](https://github.com/miyako/4d-plugin-template/commit/5a9997767fe3f6ba31e0da9ccdd1be74c891168f)
を固定しています。これは **未マージ** の
[`miyako/4d-plugin-template#30`](https://github.com/miyako/4d-plugin-template/pull/30)
ブランチ上のコミットで、正規リポジトリの `main` ではありません。
正確な固定値は `git ls-tree HEAD plugin-template` で確認できます。
ブランチが更新されても、このチェックアウトは変わりません。
既存の `4D-Plugin-SDK` gitlinkは
[`cd97d1876d4258b56d2516e8ad2816f4ee93e0b5`](https://github.com/4d/4D-Plugin-SDK/tree/cd97d1876d4258b56d2516e8ad2816f4ee93e0b5)
を維持しています。必ず再帰的にクローンしてください。

```sh
git clone --recurse-submodules https://github.com/miyako/4d-plugin-example.git
cd 4d-plugin-example
git submodule update --init --recursive
```

## ビルド

CMake 3.20以降、C++20コンパイラー、固定したSDKを使用します。
macOSではXcodeコマンドラインツールをインストールします。

```sh
cmake -S example -B example/build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" -DCMAKE_OSX_DEPLOYMENT_TARGET=11.0
cmake --build example/build --config Release --parallel
```

WindowsではC++ワークロードを備えたVisual Studio開発者シェルを使用します。

```powershell
cmake -S example -B example/build -A x64
cmake --build example/build --config Release --parallel
```

出力先は `example/example-test/Plugins/` です。macOSは `example.bundle`、
Windowsは `example/Contents/Windows64/example.4DX` とリソースを配置します。
唯一のバージョン情報源は `VERSION` で、CMakeがmacOSバンドルの両バージョン値と
`CFBundlePackageType=BNDL` を設定します。Windowsは静的CRTを使用します。
パイプラインの対象はユニバーサルmacOS（deployment target 11.0）とWindows x64です。
すべてのOS・ランタイムの組み合わせで動作確認済みという意味ではありません。
外部ライブラリ依存関係とネイティブCTestケースはありません。

## 4Dとtool4dによるテスト

互換性のある4Dで `example/example-test/Project/example.4DProject` を開き、
`test_example_greeting` を実行します。各種類、Unicode、空文字列、
ローカル時刻による選択を検証します。ヘッドレス実行では、同じアサーションを
実行して厳密な `PASS` 行を出力する `test_all` を使用します。

プロジェクトの互換性バージョンは `2101`（21.1）です。生成された
`.github/actions/tool4d-test/action.yml` は4D公式配布サービスから対応するtool4dを
取得し、macOSではホストのアーキテクチャ、Windowsではx64を選択します。
ランタイムのパッチ版はサービスの `latest` エンドポイントで解決され、
このリポジトリでは固定していません。ローカルにインストールしたtool4dの実行例：

```sh
mkdir -p example/example-test/Resources
/path/to/tool4d.app/Contents/MacOS/tool4d --dataless \
  --startup-method=test_all \
  "--project=$PWD/example/example-test/Project/example.4DProject"
```

```powershell
New-Item -ItemType Directory -Force example/example-test/Resources | Out-Null
& C:\path\to\tool4d.exe --dataless --startup-method=test_all `
  "--project=$PWD/example/example-test/Project/example.4DProject"
```

終了コード0 **かつ** 厳密な `PASS` 出力行を必須とします。
**Build and Test** はmacOS・Windowsの未署名ビルドとテストを実行し、
同一実行の成果物を統合したZIP・DMGの構造と、展開後のプラグインを検証します。
テスト専用のアドホック署名は製品署名ではありません。

## リリースアクション

| アクション | 役割 |
|---|---|
| **Bump version** | 手動でpatch/minor/majorを選択し、`main` のソース `VERSION` のみコミットします。タグ・ビルド・リリース・他ワークフローの起動は行いません。 |
| **Build** | `main` で手動起動し、version/tag/bump入力はありません。ネイティブ処理の前に不変のイベントSHA、ソースのバージョン、SDK gitlink、リリースとタグの競合を検証します。 |

**Build and Test** は別の未署名検証であり、3つ目のリリースアクションではありません。
**Pipeline drift** は利用側の整合性検証専用です。どちらも公開しません。
正規ファイル名は `.github/workflows/bump-version.yml`、`test.yml`、
`release.yml` のままです。

**Build** はテスト・組み立て・macOSのDeveloper ID署名・公証を実施し、
最終ZIP・DMGのバイト列とインストール後の動作を確認した後にだけ、
ビルドした正確なSHAに `vX.Y.Z` を公開します。既存リリース・アセットの上書きや
タグ移動は行いません。同じSHAの未公開タグは再利用できます。
タグpushでは自動公開しません。Windows配布物は未署名のままです。

署名資格情報は `release-signing` 環境に設定します。6つの必須シークレットと
環境保護については
[正規のユーザー専用ガイド](plugin-template/.github/instructions/plugin-dev.instructions.md#required-github-secrets-for-release)
を参照してください。資格情報ヘルパーを実行するのはユーザー本人のみです。
エージェントは鍵の読み取り、キーチェーンの変更、資格情報のアップロードを行いません。
資格情報の存在はリリースの許可ではありません。この実習のセットアップでは
署名・公開を起動せず、製品公証が完了したとも主張しません。

## パイプラインの再生成と確認

[AGENTS.md](AGENTS.md)、続いて
[`plugin-template/SKILL.md`](plugin-template/SKILL.md) を読んでください。
利用側の設定は `pipeline/example.json` です。
`.github/plugin-pipeline.json` は生成物であり編集元ではありません。
生成物の所有範囲は `.github/plugin-pipeline-generated.json` に記録されます。
製品ソース、英語・日本語README、エージェント入口、利用側のチェックは生成しません。

```sh
git submodule update --init --recursive
python3 plugin-template/scripts/generate_plugin_pipeline.py \
  --config pipeline/example.json --output . --update-managed
python3 scripts/check_tutorial_pipeline.py
python3 -m unittest discover -s scripts/tests -p test_tutorial_pipeline.py -v
actionlint
```

チェックはサブモジュールが初期化済みでクリーンかつインデックスのgitlinkと一致する
ことを要求し、固定した生成器の `--check` と生成された
`scripts/check_pipeline.py` を実行します。固定値不一致、正規ソースの編集、
利用側設定と生成物のずれ、想定外のワークフローを検出します。
**Pipeline drift** はCIでこの確認と失敗系回帰テストを実行します。
利用側所有の `pipeline-drift.yml` は `consumer_workflows` に明示的に宣言し、
生成器はその内容を生成・上書きしません。

正規ソースを意図的に更新するときは、レビュー済みの **公開済み** コミットを取得し、
`plugin-template` 内でdetached checkoutします。`git add plugin-template` で
gitlinkをステージし、再帰的初期化、再生成、確認を行い、固定値と生成物を一緒に
コミットしてください。`--update-managed` は手動編集された生成物の上書きを
拒否します。この保護を回避しないでください。SDKの更新は不要です。
正規のパッケージ・公開回帰テストもローカルで実行できます。

```sh
python3 -m unittest discover -s scripts/tests -v
```

これらは合成テストであり、実際の署名や公開ではありません。
