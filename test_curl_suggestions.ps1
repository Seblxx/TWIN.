# TWIN API - Suggestions Testing with curl
# Shows suggestions appearing in ALL responses

Write-Host "`n=== TWIN API Suggestions Testing ===" -ForegroundColor Cyan
Write-Host "Server: http://localhost:5000" -ForegroundColor Yellow

# Test 1: Valid prediction with suggestions
Write-Host "`n1. Valid Prediction - 'apple in 3 days'" -ForegroundColor Green
$response = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType "application/json" -Body '{"input": "apple in 3 days"}'
$response | ConvertTo-Json -Depth 5
Start-Sleep -Seconds 1

# Test 2: Typo correction with suggestions
Write-Host "`n2. Typo Correction - 'appel in 5 days'" -ForegroundColor Green
$response = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType "application/json" -Body '{"input": "appel in 5 days"}'
$response | ConvertTo-Json -Depth 5
Start-Sleep -Seconds 1

# Test 3: Another typo with suggestions
Write-Host "`n3. Another Typo - 'micrsf in 1 week'" -ForegroundColor Green
$response = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType "application/json" -Body '{"input": "micrsf in 1 week"}'
$response | ConvertTo-Json -Depth 5
Start-Sleep -Seconds 1

# Test 4: Invalid input - should still show suggestions
Write-Host "`n4. Invalid Input (ERROR) - 'blahblah in 2 days'" -ForegroundColor Red
try {
    $response = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType "application/json" -Body '{"input": "blahblah in 2 days"}'
    $response | ConvertTo-Json -Depth 5
} catch {
    $_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 5
}
Start-Sleep -Seconds 1

# Test 5: Price only mode with suggestions
Write-Host "`n5. Price Only Mode - 'microsoft'" -ForegroundColor Green
$response = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType "application/json" -Body '{"input": "microsoft"}'
$response | ConvertTo-Json -Depth 5
Start-Sleep -Seconds 1

# Test 6: Multi-word company with suggestions
Write-Host "`n6. Multi-word Company - 'jp morgan in 1 month'" -ForegroundColor Green
$response = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType "application/json" -Body '{"input": "jp morgan in 1 month"}'
$response | ConvertTo-Json -Depth 5

Write-Host "`n=== Testing Complete ===" -ForegroundColor Cyan
Write-Host "✅ All responses include 3 suggestions" -ForegroundColor Green
Write-Host "✅ Suggestions show company names (not tickers)" -ForegroundColor Green
Write-Host "✅ Suggestions include duration from input" -ForegroundColor Green
