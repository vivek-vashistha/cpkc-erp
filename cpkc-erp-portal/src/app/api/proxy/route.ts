import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    
    // Log environment variables (for debugging)
    console.log('Environment Variables:');
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('API_KEY:', API_KEY ? '***' + API_KEY.slice(-4) : 'Not set');
    
    // Build the target URL
    if (!API_BASE_URL) {
      throw new Error('API_BASE_URL environment variable is not set');
    }
    const targetUrl = new URL(API_BASE_URL);
    
    // Copy all search parameters from the request
    searchParams.forEach((value, key) => {
      targetUrl.searchParams.append(key, value);
    });
    
    // Add API key if not present
    if (!targetUrl.searchParams.has('key') && API_KEY) {
      targetUrl.searchParams.append('key', API_KEY);
    }
    
    console.log('Proxying request to:', targetUrl.toString());
    
    // Make the request to Google Apps Script
    const response = await fetch(targetUrl.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Return the data with CORS headers
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
    
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from API' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const body = await request.json();
    
    // Log environment variables (for debugging)
    console.log('POST - Environment Variables:');
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('API_KEY:', API_KEY ? '***' + API_KEY.slice(-4) : 'Not set');
    
    // Build the target URL
    if (!API_BASE_URL) {
      throw new Error('API_BASE_URL environment variable is not set');
    }
    const targetUrl = new URL(API_BASE_URL);
    
    // Copy all search parameters from the request
    searchParams.forEach((value, key) => {
      targetUrl.searchParams.append(key, value);
    });
    
    // Add API key if not present
    if (!targetUrl.searchParams.has('key') && API_KEY) {
      targetUrl.searchParams.append('key', API_KEY);
    }
    
    console.log('Proxying POST request to:', targetUrl.toString());
    
    // Make the request to Google Apps Script
    const response = await fetch(targetUrl.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Return the data with CORS headers
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
    
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from API' },
      { status: 500 }
    );
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const body = await request.json();
    
    // Log environment variables (for debugging)
    console.log('PATCH - Environment Variables:');
    console.log('API_BASE_URL:', API_BASE_URL);
    console.log('API_KEY:', API_KEY ? '***' + API_KEY.slice(-4) : 'Not set');
    
    // Build the target URL
    if (!API_BASE_URL) {
      throw new Error('API_BASE_URL environment variable is not set');
    }
    const targetUrl = new URL(API_BASE_URL);
    
    // Copy all search parameters from the request
    searchParams.forEach((value, key) => {
      targetUrl.searchParams.append(key, value);
    });
    
    // Add API key if not present
    if (!targetUrl.searchParams.has('key') && API_KEY) {
      targetUrl.searchParams.append('key', API_KEY);
    }
    
    console.log('Proxying PATCH request to:', targetUrl.toString());
    
    // Make the request to Google Apps Script
    const response = await fetch(targetUrl.toString(), {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Return the data with CORS headers
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
    
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data from API' },
      { status: 500 }
    );
  }
}
