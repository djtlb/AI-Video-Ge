import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, SafeAreaView, ActivityIndicator } from 'react-native';
import { WebView } from 'react-native-webview';
import { useState } from 'react';

export default function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // You'll need to update this URL to your FastAPI server's IP/hostname
  // For development, this could be your computer's local IP address
  // Replace with your actual server address
  const SERVER_URL = 'http://10.0.2.2:8081'; // 10.0.2.2 is special IP for Android emulator to access host's localhost

  console.log("Attempting to connect to server at:", SERVER_URL);

  const handleLoadEnd = () => {
    console.log("WebView loaded successfully");
    setLoading(false);
  };

  const handleError = (syntheticEvent) => {
    const { nativeEvent } = syntheticEvent;
    console.error('WebView error:', nativeEvent);
    setLoading(false);
    setError(true);
    setErrorMessage(nativeEvent.description || 'Unknown error');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="auto" />
      
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6366f1" />
          <Text style={styles.loadingText}>Connecting to AI Avatar Video Server...</Text>
        </View>
      )}
      
      {error && (
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Connection Error</Text>
          <Text style={styles.errorText}>
            Could not connect to the AI Avatar Video server.
            Make sure the server is running and the URL is correct.
          </Text>
          <Text style={styles.serverUrl}>Server: {SERVER_URL}</Text>
          <Text style={styles.errorDetail}>{errorMessage}</Text>
        </View>
      )}

      <WebView
        source={{ uri: SERVER_URL }}
        style={[styles.webview, loading || error ? { height: 0 } : {}]}
        onLoadEnd={handleLoadEnd}
        onError={handleError}
        javaScriptEnabled={true}
        domStorageEnabled={true}
        originWhitelist={['*']}
        useWebkit={true}
        // Disable developer mode to prevent WebSocket debug connections
        webviewDebuggingEnabled={false}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  webview: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fef2f2',
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#dc2626',
    marginBottom: 10,
  },
  errorText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  errorDetail: {
    fontSize: 12,
    color: '#666',
    padding: 10,
    backgroundColor: '#f3f4f6',
    borderRadius: 5,
    marginTop: 5,
    wordWrap: 'break-word',
    maxWidth: '100%'
  },
});
