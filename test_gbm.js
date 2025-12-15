// Test if GBM endpoint is working
const testGBM = async () => {
  try {
    const response = await fetch('http://localhost:5000/predict_plus', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: 'Tesla in 1 week',
        method: 'gbm'
      })
    });
    
    const data = await response.json();
    console.log('GBM Test Response:', data);
    console.log('Method returned:', data.method);
    console.log('Expected: gbm, Got:', data.method);
    
    if (data.method === 'gbm') {
      console.log('✅ GBM IS WORKING!');
    } else {
      console.log('❌ GBM NOT WORKING - falling back to:', data.method);
    }
  } catch (error) {
    console.error('Server error:', error);
    console.log('Make sure Flask server is running on localhost:5000');
  }
};

testGBM();
