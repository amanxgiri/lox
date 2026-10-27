param(
    [switch]$Plain,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$LoxArgs
)

$ErrorActionPreference = 'Stop'
$buildDir = Join-Path $PSScriptRoot 'build/classes'
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null
$sources = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'jlox') -Filter '*.java' |
    ForEach-Object { $_.FullName })
$sources += Join-Path $PSScriptRoot 'tool/GenerateAst.java'

& javac -encoding UTF-8 -d $buildDir @sources
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$classPath = $buildDir
$javaOptions = @()
if ($LoxArgs.Count -eq 0 -and -not $Plain -and $null -eq $env:NO_COLOR) {
    $libraryDir = Join-Path $PSScriptRoot 'build/lib'
    $jlineJar = Join-Path $libraryDir 'jline-3.30.6.jar'
    $jlineHash = 'BBC6C97167105A0ABA2DE65513C7CA4CA8FB78C0CB2875BDE44FF15101DC4EFA'
    try {
        New-Item -ItemType Directory -Force -Path $libraryDir | Out-Null
        if (-not (Test-Path -LiteralPath $jlineJar)) {
            Write-Host 'Downloading the terminal editor (first run only)...'
            $downloadPath = $jlineJar + '.download'
            Invoke-WebRequest -UseBasicParsing -Uri 'https://repo.maven.apache.org/maven2/org/jline/jline/3.30.6/jline-3.30.6.jar' -OutFile $downloadPath
            if ((Get-FileHash -LiteralPath $downloadPath -Algorithm SHA256).Hash -ne $jlineHash) {
                throw 'The terminal library checksum did not match.'
            }
            Move-Item -LiteralPath $downloadPath -Destination $jlineJar -Force
        }
        if ((Get-FileHash -LiteralPath $jlineJar -Algorithm SHA256).Hash -ne $jlineHash) {
            throw 'The terminal library checksum did not match.'
        }
        $terminalSources = @(Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot 'terminal') -Filter '*.java' |
            ForEach-Object { $_.FullName })
        $terminalClassPath = $buildDir + [IO.Path]::PathSeparator + $jlineJar
        & javac -encoding UTF-8 -cp $terminalClassPath -d $buildDir @terminalSources
        if ($LASTEXITCODE -ne 0) { throw 'Could not compile the terminal editor.' }
        $classPath = $terminalClassPath
        # Recent JDKs require explicit permission to load JLine's terminal driver.
        # Keep Java 8 compatible by adding this flag only on Java 17 or newer.
        $savedErrorActionPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $javaVersion = (& java -version 2>&1 | Out-String)
        } finally {
            $ErrorActionPreference = $savedErrorActionPreference
        }
        if ($javaVersion -match 'version "(?:1\.)?(\d+)' -and [int]$Matches[1] -ge 17) {
            $javaOptions += '--enable-native-access=ALL-UNNAMED'
        }
    } catch {
        Write-Warning "Live highlighting unavailable: $($_.Exception.Message) Using the plain prompt."
        $javaOptions += '-Dlox.noColor=true'
    }
} else {
    $javaOptions += '-Dlox.noColor=true'
}

& java @javaOptions -cp $classPath jlox.Lox @LoxArgs
exit $LASTEXITCODE
