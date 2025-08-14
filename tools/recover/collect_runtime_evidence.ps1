# Collect runtime proofs: CLI, chat, audio enumeration, tests, perf. Windows/PowerShell only.
$ErrorActionPreference = "Continue"
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
New-Item -ItemType Directory -Force -Path "tools/recover" | Out-Null

Write-Host "🧪 VPA RUNTIME EVIDENCE COLLECTION - STARTING" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Gray

$runtimeResults = @{
    "timestamp" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "cli_help" = @{}
    "chat_test" = @{}
    "audio_enum" = @{}  
    "test_run" = @{}
    "perf_baseline" = @{}
    "errors" = @()
}

try {
    # CLI Help and Timing
    Write-Host "⚡ Testing CLI functionality..." -ForegroundColor Yellow
    
    $cliStartTime = Get-Date
    $cliHelp = python -m vpa --help 2>&1
    $cliEndTime = Get-Date
    $cliDuration = ($cliEndTime - $cliStartTime).TotalMilliseconds
    
    $runtimeResults["cli_help"] = @{
        "exit_code" = $LASTEXITCODE
        "response_time_ms" = [math]::Round($cliDuration, 2)
        "output_lines" = ($cliHelp | Measure-Object -Line).Lines
        "success" = ($LASTEXITCODE -eq 0)
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ CLI help working ($([math]::Round($cliDuration,1))ms)" -ForegroundColor Green
        $cliHelp | Out-File "tools/recover/cli_help_output.txt"
    } else {
        Write-Host "   ❌ CLI help failed (exit: $LASTEXITCODE)" -ForegroundColor Red
        $runtimeResults["errors"] += "CLI help command failed"
    }

    # Chat Test (if LLM enabled)
    Write-Host "💬 Testing chat functionality..." -ForegroundColor Yellow
    
    $env:VPA_ENABLE_LLM = "1"
    $chatStartTime = Get-Date
    $chatResult = python -m vpa --chat "test message" 2>&1
    $chatEndTime = Get-Date
    $chatDuration = ($chatEndTime - $chatStartTime).TotalMilliseconds
    
    $runtimeResults["chat_test"] = @{
        "exit_code" = $LASTEXITCODE  
        "response_time_ms" = [math]::Round($chatDuration, 2)
        "output_length" = ($chatResult | Measure-Object -Character).Characters
        "success" = ($LASTEXITCODE -eq 0)
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Chat functionality working ($([math]::Round($chatDuration,1))ms)" -ForegroundColor Green
        $chatResult | Out-File "tools/recover/chat_test_output.txt"
    } else {
        Write-Host "   ⚠️ Chat test failed (exit: $LASTEXITCODE) - may be expected without API keys" -ForegroundColor Yellow
        $runtimeResults["errors"] += "Chat test failed - likely missing API keys"
    }

    # Audio System Enumeration
    Write-Host "🎤 Testing audio system..." -ForegroundColor Yellow
    
    $audioStartTime = Get-Date
    $audioEnum = python -c "
import sys
sys.path.insert(0, 'src')
try:
    from vpa.audio.stt_entry import run_stt
    import speech_recognition as sr
    r = sr.Recognizer()
    mics = sr.Microphone.list_microphone_names()
    print(f'Microphones found: {len(mics)}')
    for i, mic in enumerate(mics[:10]):  # Limit to first 10
        print(f'{i}: {mic}')
    print('Audio system: READY')
except Exception as e:
    print(f'Audio system error: {e}')
    sys.exit(1)
" 2>&1
    $audioEndTime = Get-Date
    $audioDuration = ($audioEndTime - $audioStartTime).TotalMilliseconds
    
    $runtimeResults["audio_enum"] = @{
        "exit_code" = $LASTEXITCODE
        "response_time_ms" = [math]::Round($audioDuration, 2)
        "microphone_count" = 0
        "success" = ($LASTEXITCODE -eq 0)
    }
    
    if ($LASTEXITCODE -eq 0) {
        # Parse microphone count
        $micCountLine = $audioEnum | Select-String "Microphones found: (\d+)"
        if ($micCountLine) {
            $runtimeResults["audio_enum"]["microphone_count"] = [int]$micCountLine.Matches[0].Groups[1].Value
        }
        
        Write-Host "   ✅ Audio enumeration successful ($($runtimeResults["audio_enum"]["microphone_count"]) mics, $([math]::Round($audioDuration,1))ms)" -ForegroundColor Green
        $audioEnum | Out-File "tools/recover/audio_enum_output.txt"
    } else {
        Write-Host "   ❌ Audio enumeration failed (exit: $LASTEXITCODE)" -ForegroundColor Red
        $runtimeResults["errors"] += "Audio system enumeration failed"
    }

    # Test Collection and Execution
    Write-Host "🧪 Running test collection..." -ForegroundColor Yellow
    
    $testStartTime = Get-Date
    $testCollection = python -m pytest --collect-only -q 2>&1
    $testCollectExit = $LASTEXITCODE
    $testEndTime = Get-Date
    $testDuration = ($testEndTime - $testStartTime).TotalMilliseconds
    
    # Parse test count
    $testCount = 0
    $testCountLine = $testCollection | Select-String "(\d+) tests? collected"
    if ($testCountLine) {
        $testCount = [int]$testCountLine.Matches[0].Groups[1].Value
    }
    
    $runtimeResults["test_run"] = @{
        "collection_exit_code" = $testCollectExit
        "collection_time_ms" = [math]::Round($testDuration, 2)
        "tests_collected" = $testCount
        "collection_success" = ($testCollectExit -eq 0)
    }
    
    if ($testCollectExit -eq 0) {
        Write-Host "   ✅ Test collection successful ($testCount tests, $([math]::Round($testDuration,1))ms)" -ForegroundColor Green
        
        # Run a quick smoke test (core tests only)
        Write-Host "   Running core smoke tests..." -ForegroundColor Gray
        
        $smokeStartTime = Get-Date
        $smokeTest = python -m pytest tests/test_core_architecture.py -v --tb=short 2>&1
        $smokeExit = $LASTEXITCODE
        $smokeEndTime = Get-Date
        $smokeDuration = ($smokeEndTime - $smokeStartTime).TotalMilliseconds
        
        $runtimeResults["test_run"]["smoke_exit_code"] = $smokeExit
        $runtimeResults["test_run"]["smoke_time_ms"] = [math]::Round($smokeDuration, 2)
        $runtimeResults["test_run"]["smoke_success"] = ($smokeExit -eq 0)
        
        if ($smokeExit -eq 0) {
            Write-Host "   ✅ Smoke tests passed ($([math]::Round($smokeDuration,1))ms)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ Smoke tests failed (exit: $smokeExit)" -ForegroundColor Yellow
        }
        
        $testCollection | Out-File "tools/recover/test_collection_output.txt"
        $smokeTest | Out-File "tools/recover/smoke_test_output.txt"
    } else {
        Write-Host "   ❌ Test collection failed (exit: $testCollectExit)" -ForegroundColor Red
        $runtimeResults["errors"] += "Test collection failed"
    }

    # Performance Baseline
    Write-Host "⚡ Collecting performance baseline..." -ForegroundColor Yellow
    
    $perfStartTime = Get-Date
    $perfTest = python -c "
import sys, time, psutil, os
sys.path.insert(0, 'src')

start_time = time.time()
start_memory = psutil.Process().memory_info().rss / 1024 / 1024

try:
    import src.vpa.core.app
    import_time = time.time() - start_time
    
    # Get memory after import
    post_import_memory = psutil.Process().memory_info().rss / 1024 / 1024
    memory_delta = post_import_memory - start_memory
    
    print(f'Import time: {import_time*1000:.1f}ms')
    print(f'Memory usage: {post_import_memory:.1f}MB (delta: +{memory_delta:.1f}MB)')
    print(f'Python version: {sys.version.split()[0]}')
    print(f'Working directory: {os.getcwd()}')
    print('Performance baseline: COLLECTED')
    
except Exception as e:
    print(f'Performance test error: {e}')
    sys.exit(1)
" 2>&1
    $perfEndTime = Get-Date  
    $perfDuration = ($perfEndTime - $perfStartTime).TotalMilliseconds
    
    $runtimeResults["perf_baseline"] = @{
        "exit_code" = $LASTEXITCODE
        "test_duration_ms" = [math]::Round($perfDuration, 2)
        "import_time_ms" = 0
        "memory_usage_mb" = 0
        "success" = ($LASTEXITCODE -eq 0)
    }
    
    if ($LASTEXITCODE -eq 0) {
        # Parse performance metrics
        $importTimeLine = $perfTest | Select-String "Import time: ([\d.]+)ms"
        if ($importTimeLine) {
            $runtimeResults["perf_baseline"]["import_time_ms"] = [float]$importTimeLine.Matches[0].Groups[1].Value
        }
        
        $memoryLine = $perfTest | Select-String "Memory usage: ([\d.]+)MB"
        if ($memoryLine) {
            $runtimeResults["perf_baseline"]["memory_usage_mb"] = [float]$memoryLine.Matches[0].Groups[1].Value
        }
        
        Write-Host "   ✅ Performance baseline collected (import: $($runtimeResults["perf_baseline"]["import_time_ms"])ms, memory: $($runtimeResults["perf_baseline"]["memory_usage_mb"])MB)" -ForegroundColor Green
        $perfTest | Out-File "tools/recover/perf_baseline_output.txt"
    } else {
        Write-Host "   ❌ Performance baseline failed (exit: $LASTEXITCODE)" -ForegroundColor Red
        $runtimeResults["errors"] += "Performance baseline collection failed"
    }

} catch {
    Write-Host "❌ Critical error during runtime collection: $($_.Exception.Message)" -ForegroundColor Red
    $runtimeResults["errors"] += "Critical runtime collection error: $($_.Exception.Message)"
}

# Write runtime results
$runtimeResults | ConvertTo-Json -Depth 3 | Out-File "tools/recover/runtime_evidence.json"

# Generate performance baseline markdown
$perfReport = @"
# VPA Performance Baseline

**Generated**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Phase**: Runtime Evidence Collection

## 📊 **PERFORMANCE METRICS**

| Metric | Value | Target | Status |
|--------|-------|---------|--------|
| CLI Response Time | $($runtimeResults["cli_help"]["response_time_ms"])ms | <1000ms | $(if($runtimeResults["cli_help"]["response_time_ms"] -lt 1000){"✅ PASS"}else{"⚠️ SLOW"}) |
| Chat Response Time | $($runtimeResults["chat_test"]["response_time_ms"])ms | <5000ms | $(if($runtimeResults["chat_test"]["response_time_ms"] -lt 5000){"✅ PASS"}else{"⚠️ SLOW"}) |
| Import Time | $($runtimeResults["perf_baseline"]["import_time_ms"])ms | <2000ms | $(if($runtimeResults["perf_baseline"]["import_time_ms"] -lt 2000){"✅ PASS"}else{"⚠️ SLOW"}) |
| Memory Usage | $($runtimeResults["perf_baseline"]["memory_usage_mb"])MB | <100MB | $(if($runtimeResults["perf_baseline"]["memory_usage_mb"] -lt 100){"✅ PASS"}else{"⚠️ HIGH"}) |
| Test Collection | $($runtimeResults["test_run"]["collection_time_ms"])ms | <10000ms | $(if($runtimeResults["test_run"]["collection_time_ms"] -lt 10000){"✅ PASS"}else{"⚠️ SLOW"}) |

## 🎯 **SYSTEM VALIDATION**

- **CLI Help**: $(if($runtimeResults["cli_help"]["success"]){"✅ Working"}else{"❌ Failed"}) ($($runtimeResults["cli_help"]["output_lines"]) lines)
- **Chat System**: $(if($runtimeResults["chat_test"]["success"]){"✅ Working"}else{"⚠️ Limited"}) (LLM integration)
- **Audio System**: $(if($runtimeResults["audio_enum"]["success"]){"✅ Working"}else{"❌ Failed"}) ($($runtimeResults["audio_enum"]["microphone_count"]) microphones)
- **Test Collection**: $(if($runtimeResults["test_run"]["collection_success"]){"✅ Working"}else{"❌ Failed"}) ($($runtimeResults["test_run"]["tests_collected"]) tests)
- **Smoke Tests**: $(if($runtimeResults["test_run"]["smoke_success"]){"✅ Passed"}else{"⚠️ Failed"})

## 🚀 **PERFORMANCE SUMMARY**

$(if($runtimeResults["errors"].Count -eq 0) {
"✅ **All systems operational** - VPA runtime validation successful"
} else {
"⚠️ **$($runtimeResults["errors"].Count) issues detected** - See error details below"
})

### Error Details:
$(if($runtimeResults["errors"].Count -gt 0) {
$runtimeResults["errors"] | ForEach-Object { "- $_" }
} else {
"*No errors detected*"
})

---
*Runtime evidence collection completed. System ready for production validation.*
"@

$perfReport | Out-File "PERF_BASELINE.md"

# Summary Report
Write-Host "`n=================================================================" -ForegroundColor Gray
Write-Host "🧪 RUNTIME EVIDENCE SUMMARY" -ForegroundColor Cyan

Write-Host "   CLI Functionality: $(if($runtimeResults["cli_help"]["success"]){"✅ WORKING"}else{"❌ FAILED"})" -ForegroundColor $(if($runtimeResults["cli_help"]["success"]){"Green"}else{"Red"})
Write-Host "   Chat System: $(if($runtimeResults["chat_test"]["success"]){"✅ WORKING"}else{"⚠️ LIMITED"})" -ForegroundColor $(if($runtimeResults["chat_test"]["success"]){"Green"}else{"Yellow"})
Write-Host "   Audio System: $(if($runtimeResults["audio_enum"]["success"]){"✅ WORKING"}else{"❌ FAILED"})" -ForegroundColor $(if($runtimeResults["audio_enum"]["success"]){"Green"}else{"Red"})
Write-Host "   Test Collection: $(if($runtimeResults["test_run"]["collection_success"]){"✅ WORKING"}else{"❌ FAILED"})" -ForegroundColor $(if($runtimeResults["test_run"]["collection_success"]){"Green"}else{"Red"})
Write-Host "   Performance: $(if($runtimeResults["perf_baseline"]["success"]){"✅ BASELINE"}else{"❌ FAILED"})" -ForegroundColor $(if($runtimeResults["perf_baseline"]["success"]){"Green"}else{"Red"})

Write-Host "`n📊 KEY METRICS:"
Write-Host "   Import Time: $($runtimeResults["perf_baseline"]["import_time_ms"])ms" -ForegroundColor Cyan
Write-Host "   Memory Usage: $($runtimeResults["perf_baseline"]["memory_usage_mb"])MB" -ForegroundColor Cyan  
Write-Host "   Microphones: $($runtimeResults["audio_enum"]["microphone_count"])" -ForegroundColor Cyan
Write-Host "   Tests Collected: $($runtimeResults["test_run"]["tests_collected"])" -ForegroundColor Cyan
Write-Host "   Total Errors: $($runtimeResults["errors"].Count)" -ForegroundColor $(if($runtimeResults["errors"].Count -eq 0){"Green"}else{"Red"})

Write-Host "`n📄 EVIDENCE FILES:"
$evidenceFiles = @(
    "tools/recover/runtime_evidence.json",
    "tools/recover/cli_help_output.txt", 
    "tools/recover/chat_test_output.txt",
    "tools/recover/audio_enum_output.txt",
    "tools/recover/test_collection_output.txt",
    "tools/recover/perf_baseline_output.txt",
    "PERF_BASELINE.md"
)

foreach ($file in $evidenceFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "   ✅ $file ($([math]::Round($size/1024,1))KB)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file (missing)" -ForegroundColor Yellow
    }
}

Write-Host "`n🎯 READY FOR: PR #18 status update with comprehensive evidence" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Gray

# Return appropriate exit code
if ($runtimeResults["errors"].Count -eq 0) {
    exit 0
} else {
    exit 1
}
