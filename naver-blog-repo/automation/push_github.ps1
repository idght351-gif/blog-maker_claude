# 이 폴더 전체를 GitHub(idght351-gif/blog-maker_claude)의 naver-blog-repo/ 폴더로 올립니다.
# 원격 저장소는 naver-blog-repo/ 하위 폴더 구조라서, 로컬 파일을 그 경로로 옮긴 트리를 만들어 원격 main 위에 커밋합니다.
# .gitignore 에 있는 비밀 파일(.state/), 사진(photos/), node_modules 는 올라가지 않습니다.
# 사용법: powershell -ExecutionPolicy Bypass -File automation\push_github.ps1 "커밋 메시지"
param([string]$Message = "업데이트")
$ErrorActionPreference = "Stop"
$env:Path = "C:\Program Files\Git\cmd;$env:Path"
Set-Location (Split-Path -Parent $PSScriptRoot)
git fetch -q origin
git add -A
$tree = git write-tree
$env:GIT_INDEX_FILE = ".git/index.prefixed"
git read-tree --empty
git read-tree --prefix=naver-blog-repo/ $tree
$prefixed = git write-tree
Remove-Item Env:GIT_INDEX_FILE; Remove-Item .git/index.prefixed
if ($prefixed -eq (git rev-parse "origin/main^{tree}")) { Write-Output "바뀐 것이 없습니다."; exit 0 }
git diff --stat origin/main $prefixed
$commit = git commit-tree $prefixed -p origin/main -m $Message
git update-ref refs/heads/main $commit
git push origin main
