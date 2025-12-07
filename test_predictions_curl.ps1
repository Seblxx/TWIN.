# Test script for predictions API with Authentication

Write-Host "`n=== Testing Predictions API with Authentication ===" -ForegroundColor Cyan

# Test Account 1: dazrini@gmail.com
Write-Host "`n--- Testing with Account 1: dazrini@gmail.com ---" -ForegroundColor Magenta

# Login to get token
Write-Host "`n1. Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "dazrini@gmail.com"
    password = "gummybear"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/login" -Method POST -ContentType "application/json" -Body $loginBody
    $token = $loginResponse.token
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    Write-Host "   SUCCESS: Logged in as dazrini@gmail.com" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Create prediction for AAPL
Write-Host "`n2. Creating prediction for AAPL (1 Week)..." -ForegroundColor Yellow
$aaplBody = @{
    input = "AAPL in 1 week"
} | ConvertTo-Json

try {
    $aaplResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/predict" -Method POST -ContentType "application/json" -Body $aaplBody
    Write-Host "   SUCCESS: AAPL prediction created" -ForegroundColor Green
    Write-Host "   Stock: $($aaplResponse.stock)" -ForegroundColor White
    Write-Host "   Current Price: `$$($aaplResponse.lastClose)" -ForegroundColor White
    Write-Host "   Predicted Price: `$$($aaplResponse.result)" -ForegroundColor White
    Write-Host "   Method: $($aaplResponse.method)" -ForegroundColor White
    
    # Save prediction to backend
    $savePredBody = @{
        stock = $aaplResponse.stock
        duration = $aaplResponse.duration
        lastClose = $aaplResponse.lastClose
        predictedPrice = $aaplResponse.result
        method = $aaplResponse.method
        delta = $aaplResponse.result - $aaplResponse.lastClose
        pct = (($aaplResponse.result - $aaplResponse.lastClose) / $aaplResponse.lastClose) * 100
    } | ConvertTo-Json
    
    $saveResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/predictions/save" -Method POST -Headers $headers -Body $savePredBody
    Write-Host "   Prediction saved to backend" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Create prediction for MSFT
Write-Host "`n3. Creating prediction for MSFT (1 Month)..." -ForegroundColor Yellow
$msftBody = @{
    input = "Microsoft in 1 month"
} | ConvertTo-Json

try {
    $msftResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/predict" -Method POST -ContentType "application/json" -Body $msftBody
    Write-Host "   SUCCESS: MSFT prediction created" -ForegroundColor Green
    Write-Host "   Stock: $($msftResponse.stock)" -ForegroundColor White
    Write-Host "   Current Price: `$$($msftResponse.lastClose)" -ForegroundColor White
    Write-Host "   Predicted Price: `$$($msftResponse.result)" -ForegroundColor White
    
    # Save prediction
    $savePredBody = @{
        stock = $msftResponse.stock
        duration = $msftResponse.duration
        lastClose = $msftResponse.lastClose
        predictedPrice = $msftResponse.result
        method = $msftResponse.method
        delta = $msftResponse.result - $msftResponse.lastClose
        pct = (($msftResponse.result - $msftResponse.lastClose) / $msftResponse.lastClose) * 100
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/predictions/save" -Method POST -Headers $headers -Body $savePredBody | Out-Null
    Write-Host "   Prediction saved to backend" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Create prediction for GOOGL
Write-Host "`n4. Creating prediction for GOOGL (3 Months)..." -ForegroundColor Yellow
$googlBody = @{
    input = "Google in 3 months"
} | ConvertTo-Json

try {
    $googlResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/predict" -Method POST -ContentType "application/json" -Body $googlBody
    Write-Host "   SUCCESS: GOOGL prediction created" -ForegroundColor Green
    Write-Host "   Stock: $($googlResponse.stock)" -ForegroundColor White
    Write-Host "   Current Price: `$$($googlResponse.lastClose)" -ForegroundColor White
    Write-Host "   Predicted Price: `$$($googlResponse.result)" -ForegroundColor White
    
    # Save prediction
    $savePredBody = @{
        stock = $googlResponse.stock
        duration = $googlResponse.duration
        lastClose = $googlResponse.lastClose
        predictedPrice = $googlResponse.result
        method = $googlResponse.method
        delta = $googlResponse.result - $googlResponse.lastClose
        pct = (($googlResponse.result - $googlResponse.lastClose) / $googlResponse.lastClose) * 100
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/predictions/save" -Method POST -Headers $headers -Body $savePredBody | Out-Null
    Write-Host "   Prediction saved to backend" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Fetch user predictions
Write-Host "`n5. Fetching user predictions..." -ForegroundColor Yellow
try {
    $predictions = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/predictions/user" -Method GET -Headers $headers
    Write-Host "   SUCCESS: Retrieved $($predictions.Count) predictions" -ForegroundColor Green
    
    if ($predictions.Count -gt 0) {
        Write-Host "`n   Predictions Summary:" -ForegroundColor Cyan
        foreach ($pred in $predictions) {
            $changeIcon = if ($pred.predictedPrice -gt $pred.lastClose) { "UP" } else { "DOWN" }
            $pctFormatted = "{0:N2}" -f $pred.pct
            Write-Host "   [$changeIcon] $($pred.stock) ($($pred.duration)): `$$($pred.lastClose) -> `$$($pred.predictedPrice) ($pctFormatted%)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n`n--- Testing with Account 2: test2@gmail.com ---" -ForegroundColor Magenta

# Login with second account
Write-Host "`n6. Logging in as test2..." -ForegroundColor Yellow
$loginBody2 = @{
    email = "test2@gmail.com"
    password = "password"
} | ConvertTo-Json

try {
    $loginResponse2 = Invoke-RestMethod -Uri "http://127.0.0.1:5000/login" -Method POST -ContentType "application/json" -Body $loginBody2
    $token2 = $loginResponse2.token
    $headers2 = @{
        "Authorization" = "Bearer $token2"
        "Content-Type" = "application/json"
    }
    Write-Host "   SUCCESS: Logged in as test2@gmail.com" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 7: Create prediction for TSLA
Write-Host "`n7. Creating prediction for TSLA..." -ForegroundColor Yellow
$tslaBody = @{
    input = "Tesla in 2 weeks"
} | ConvertTo-Json

try {
    $tslaResponse = Invoke-RestMethod -Uri "http://127.0.0.1:5000/predict" -Method POST -ContentType "application/json" -Body $tslaBody
    Write-Host "   SUCCESS: TSLA prediction created" -ForegroundColor Green
    Write-Host "   Stock: $($tslaResponse.stock)" -ForegroundColor White
    Write-Host "   Current Price: `$$($tslaResponse.lastClose)" -ForegroundColor White
    Write-Host "   Predicted Price: `$$($tslaResponse.result)" -ForegroundColor White
    
    # Save prediction
    $savePredBody = @{
        stock = $tslaResponse.stock
        duration = $tslaResponse.duration
        lastClose = $tslaResponse.lastClose
        predictedPrice = $tslaResponse.result
        method = $tslaResponse.method
        delta = $tslaResponse.result - $tslaResponse.lastClose
        pct = (($tslaResponse.result - $tslaResponse.lastClose) / $tslaResponse.lastClose) * 100
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/predictions/save" -Method POST -Headers $headers2 -Body $savePredBody | Out-Null
    Write-Host "   Prediction saved to backend" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Fetch test2 predictions
Write-Host "`n8. Fetching test2 predictions..." -ForegroundColor Yellow
try {
    $predictions2 = Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/predictions/user" -Method GET -Headers $headers2
    Write-Host "   SUCCESS: Retrieved $($predictions2.Count) predictions for test2" -ForegroundColor Green
    
    if ($predictions2.Count -gt 0) {
        Write-Host "`n   Predictions Summary:" -ForegroundColor Cyan
        foreach ($pred in $predictions2) {
            $changeIcon = if ($pred.predictedPrice -gt $pred.lastClose) { "UP" } else { "DOWN" }
            $pctFormatted = "{0:N2}" -f $pred.pct
            Write-Host "   [$changeIcon] $($pred.stock) ($($pred.duration)): `$$($pred.lastClose) -> `$$($pred.predictedPrice) ($pctFormatted%)" -ForegroundColor White
        }
    }
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== All Tests Complete ===" -ForegroundColor Cyan
Write-Host "`nTest Results:" -ForegroundColor Yellow
Write-Host "  - Account 1 (dazrini@gmail.com): $($predictions.Count) predictions" -ForegroundColor White
Write-Host "  - Account 2 (test2@gmail.com): $($predictions2.Count) predictions" -ForegroundColor White
Write-Host "`nNow login to http://127.0.0.1:5000/predictions.html to verify display" -ForegroundColor Yellow
Write-Host "  Use: dazrini@gmail.com / gummybear" -ForegroundColor Gray
Write-Host "  Or:  test2@gmail.com / password`n" -ForegroundColor Gray
