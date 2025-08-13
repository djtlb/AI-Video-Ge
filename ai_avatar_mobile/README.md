# AI Avatar Video Mobile App

A Flutter-based mobile application for generating AI avatar videos. This app allows users to browse through avatars and create videos with synthesized speech.

## Features

- Browse available AI avatars
- Create videos with custom text for avatars to speak
- View videos in a library
- Offline support for viewing avatars and videos
- Connectivity status indicators
- Error handling and recovery

## Prerequisites

- Flutter SDK (v3.19.3 or later)
- Android SDK (API level 34 or later)
- Java JDK 17

## Dependencies

- http: For API communication
- video_player: For playing generated videos
- path_provider: For managing file paths
- shared_preferences: For local storage
- flutter_cache_manager: For caching assets
- connectivity_plus: For checking internet connectivity

## Project Structure

```dart
lib/
  ├── models/
  │   ├── avatar.dart
  │   └── video.dart
  ├── screens/
  │   ├── home_screen.dart
  │   ├── create_video_screen.dart
  │   ├── video_preview_screen.dart
  │   └── video_library_screen.dart
  ├── services/
  │   ├── api_service.dart
  │   ├── local_storage_service.dart
  │   └── data_service.dart
  ├── utils/
  │   └── connectivity_util.dart
  └── main.dart
```

## Setup

1. Clone the repository
2. Ensure Flutter and Android SDK are installed
3. Run `flutter pub get` to install dependencies
4. Update the API base URL in `main.dart` to point to your backend server

## Running the App

```bash
cd ai_avatar_mobile
flutter run
```

For Android emulator, the app is configured to connect to `http://10.0.2.2:8000` by default, which points to `localhost:8000` on your host machine.

## Backend API

The app expects a backend API with the following endpoints:

- `GET /avatars` - Get list of avatars
- `GET /avatars/{id}` - Get avatar details
- `GET /videos` - Get list of videos
- `POST /videos` - Create a new video
- `GET /videos/{id}` - Get video status and details

## Offline Support

The app implements a comprehensive offline strategy:

1. All avatars and videos are cached locally
2. Network connectivity is monitored
3. UI indicates offline status
4. App falls back to cached data when offline
5. Video creation is disabled when offline
