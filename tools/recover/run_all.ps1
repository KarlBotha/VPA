# Orchestrate evidence harvest and consolidation. Windows/PowerShell only.
# Usage: pwsh -ExecutionPolicy Bypass -File tools/recover/run_all.ps1 [-Deep]
param([switch]$Deep)

$ErrorActionPreference = "Continue"
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Out-File:Width'] = 200

Write-Host "🔍 VPA EVIDENCE HARVEST + RUNTIME PROOF - STARTING" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Gray

# Create output directory
New-Item -ItemType Directory -Force -Path "tools/recover" | Out-Null

# Initialize harvest status tracking
$HarvestStatus = @{
    "archive_scan" = "NOT_STARTED"
    "local_scan" = "NOT_STARTED" 
    "consolidation" = "NOT_STARTED"
    "total_errors" = 0
    "components_found" = 0
    "local_evidence_files" = 0
}

try {
    # Step 1: Archive Recovery Scan
    Write-Host "📁 Step 1: Archive Recovery Scan..." -ForegroundColor Yellow
    
    $archiveResult = python tools/recover/scan_archives.py
    $archiveExit = $LASTEXITCODE
    
    if ($archiveExit -eq 0) {
        $HarvestStatus["archive_scan"] = "SUCCESS"
        Write-Host "✅ Archive scan completed successfully" -ForegroundColor Green
        
        # Parse component count if available
        if (Test-Path "tools/recover/recover_map.json") {
            $archiveMap = Get-Content "tools/recover/recover_map.json" | ConvertFrom-Json
            $HarvestStatus["components_found"] = ($archiveMap.PSObject.Properties).Count
            Write-Host "   Found $($HarvestStatus["components_found"]) component types in archives" -ForegroundColor Green
        }
    } else {
        $HarvestStatus["archive_scan"] = "FAILED"
        $HarvestStatus["total_errors"]++
        Write-Host "❌ Archive scan failed (exit code: $archiveExit)" -ForegroundColor Red
    }

    # Step 2: Local Evidence Harvest  
    Write-Host "🏠 Step 2: Local Evidence Harvest..." -ForegroundColor Yellow
    
    $localResult = python tools/recover/scan_local.py
    $localExit = $LASTEXITCODE
    
    if ($localExit -eq 0) {
        $HarvestStatus["local_scan"] = "SUCCESS"
        Write-Host "✅ Local scan completed successfully" -ForegroundColor Green
        
        # Parse local evidence count if available
        if (Test-Path "tools/recover/local_candidates.json") {
            $localMap = Get-Content "tools/recover/local_candidates.json" | ConvertFrom-Json
            $totalLocalFiles = 0
            foreach ($pattern in $localMap.PSObject.Properties) {
                $totalLocalFiles += $pattern.Value.Count
            }
            $HarvestStatus["local_evidence_files"] = $totalLocalFiles
            Write-Host "   Found $totalLocalFiles local evidence files" -ForegroundColor Green
        }
    } else {
        $HarvestStatus["local_scan"] = "FAILED"
        $HarvestStatus["total_errors"]++
        Write-Host "❌ Local scan failed (exit code: $localExit)" -ForegroundColor Red
    }

    # Step 3: Consolidation
    Write-Host "📊 Step 3: Report Consolidation..." -ForegroundColor Yellow
    
    $consolidateResult = python tools/recover/consolidate_reports.py
    $consolidateExit = $LASTEXITCODE
    
    if ($consolidateExit -eq 0) {
        $HarvestStatus["consolidation"] = "SUCCESS"
        Write-Host "✅ Consolidation completed successfully" -ForegroundColor Green
    } else {
        $HarvestStatus["consolidation"] = "FAILED"
        $HarvestStatus["total_errors"]++
        Write-Host "❌ Consolidation failed (exit code: $consolidateExit)" -ForegroundColor Red
    }

    # Deep Scan Enhancement (if requested)
    if ($Deep) {
        Write-Host "🔬 Deep Scan Mode: Enhanced Evidence Collection..." -ForegroundColor Magenta
        
        # Scan for additional file types
        Write-Host "   Scanning for config files, logs, and documentation..." -ForegroundColor Gray
        
        $deepResults = @()
        
        # Look for VPA-related files in common locations
        $searchPaths = @(
            "$env:APPDATA",
            "$env:LOCALAPPDATA", 
            "$env:USERPROFILE\Documents",
            "$env:USERPROFILE\Desktop"
        )
        
        foreach ($path in $searchPaths) {
            if (Test-Path $path) {
                $vpaFiles = Get-ChildItem -Path $path -Recurse -Include "*.json","*.yaml","*.yml","*.ini","*.cfg","*.log" -ErrorAction SilentlyContinue | 
                           Where-Object { $_.Name -match "vpa|VPA" -or (Get-Content $_.FullName -ErrorAction SilentlyContinue | Select-String "vpa|VPA" -Quiet) } |
                           Select-Object -First 20
                
                foreach ($file in $vpaFiles) {
                    $deepResults += @{
                        "path" = $file.FullName
                        "size" = $file.Length
                        "modified" = $file.LastWriteTime
                    }
                }
            }
        }
        
        if ($deepResults.Count -gt 0) {
            # Write deep scan results
            $deepResults | ConvertTo-Json -Depth 3 | Out-File "tools/recover/deep_scan_results.json"
            Write-Host "   Deep scan found $($deepResults.Count) additional VPA files" -ForegroundColor Green
        } else {
            Write-Host "   Deep scan found no additional VPA files" -ForegroundColor Yellow
        }
    }

} catch {
    Write-Host "❌ Critical error during harvest: $($_.Exception.Message)" -ForegroundColor Red
    $HarvestStatus["total_errors"]++
}

# Write harvest status
$HarvestStatus | ConvertTo-Json -Depth 2 | Out-File "tools/recover/HARVEST_STATUS.txt"

# Summary Report
Write-Host "`n=================================================================" -ForegroundColor Gray
Write-Host "📋 EVIDENCE HARVEST SUMMARY" -ForegroundColor Cyan

Write-Host "   Archive Scan: $($HarvestStatus["archive_scan"])" -ForegroundColor $(if($HarvestStatus["archive_scan"] -eq "SUCCESS"){"Green"}else{"Red"})
Write-Host "   Local Scan: $($HarvestStatus["local_scan"])" -ForegroundColor $(if($HarvestStatus["local_scan"] -eq "SUCCESS"){"Green"}else{"Red"})
Write-Host "   Consolidation: $($HarvestStatus["consolidation"])" -ForegroundColor $(if($HarvestStatus["consolidation"] -eq "SUCCESS"){"Green"}else{"Red"})

Write-Host "`n📊 HARVEST METRICS:"
Write-Host "   Components Found: $($HarvestStatus["components_found"])" -ForegroundColor Cyan
Write-Host "   Local Evidence: $($HarvestStatus["local_evidence_files"]) files" -ForegroundColor Cyan
Write-Host "   Total Errors: $($HarvestStatus["total_errors"])" -ForegroundColor $(if($HarvestStatus["total_errors"] -eq 0){"Green"}else{"Red"})

# List generated files
Write-Host "`n📄 GENERATED FILES:"
$outputFiles = @(
    "RECOVERY_REPORT.md",
    "RECOVERY_REPORT_LOCAL.md", 
    "CONSOLIDATED_RECOVERY_REPORT.md",
    "tools/recover/recover_map.json",
    "tools/recover/local_candidates.json",
    "tools/recover/consolidated_map.json",
    "tools/recover/HARVEST_STATUS.txt"
)

foreach ($file in $outputFiles) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "   ✅ $file ($([math]::Round($size/1024,1))KB)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file (missing)" -ForegroundColor Red
    }
}

if ($Deep -and (Test-Path "tools/recover/deep_scan_results.json")) {
    $deepSize = (Get-Item "tools/recover/deep_scan_results.json").Length
    Write-Host "   ✅ tools/recover/deep_scan_results.json ($([math]::Round($deepSize/1024,1))KB)" -ForegroundColor Green
}

Write-Host "`n🎯 NEXT STEP: Run collect_runtime_evidence.ps1" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Gray

# Return appropriate exit code
if ($HarvestStatus["total_errors"] -eq 0) {
    exit 0
} else {
    exit 1
}
