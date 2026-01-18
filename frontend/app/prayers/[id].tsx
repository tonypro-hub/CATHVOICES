import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, Alert, Dimensions, Platform } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Clipboard from '@react-native-clipboard/clipboard';
import { WebView } from 'react-native-webview';
import axios from 'axios';

const BRAND_COLORS = {
  burgundy: '#8B0000',
  gold: '#D4AF37',
  cream: '#F5F5DC',
  dark: '#1A1A1A',
  white: '#FFFFFF',
};

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const { width } = Dimensions.get('window');

interface Prayer {
  id: string;
  title: string;
  videoId: string;
  prayerText: string;
  category: string;
}

export default function PrayerDetailScreen() {
  const { id } = useLocalSearchParams();
  const [prayer, setPrayer] = useState<Prayer | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchPrayer();
  }, [id]);

  const fetchPrayer = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/prayers/${id}`);
      setPrayer(response.data);
    } catch (error) {
      console.error('Error fetching prayer:', error);
      Alert.alert('Error', 'Failed to load prayer. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = () => {
    if (prayer) {
      Clipboard.setString(prayer.prayerText);
      setCopied(true);
      Alert.alert('Copied!', 'Prayer text copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={BRAND_COLORS.gold} />
          <Text style={styles.loadingText}>Loading prayer...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!prayer) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={64} color={BRAND_COLORS.gold} />
          <Text style={styles.errorText}>Prayer not found</Text>
        </View>
      </SafeAreaView>
    );
  }

  // Generate YouTube embed HTML
  const getYouTubeEmbedHTML = (videoId: string) => {
    return `
      <!DOCTYPE html>
      <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
          <style>
            * { margin: 0; padding: 0; }
            body { background: #000; }
            .video-container {
              position: relative;
              padding-bottom: 56.25%;
              height: 0;
              overflow: hidden;
            }
            .video-container iframe {
              position: absolute;
              top: 0;
              left: 0;
              width: 100%;
              height: 100%;
            }
          </style>
        </head>
        <body>
          <div class="video-container">
            <iframe
              src="https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </body>
      </html>
    `;
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Video Section */}
        <View style={styles.videoContainer}>
          <WebView
            style={styles.video}
            source={{ html: getYouTubeEmbedHTML(prayer.videoId) }}
            allowsFullscreenVideo={true}
            javaScriptEnabled={true}
            domStorageEnabled={true}
            mediaPlaybackRequiresUserAction={false}
          />
        </View>

        {/* Prayer Header */}
        <View style={styles.prayerHeader}>
          <Text style={styles.prayerCategory}>{prayer.category}</Text>
          <Text style={styles.prayerTitle}>{prayer.title}</Text>
        </View>

        {/* Copy Button */}
        <View style={styles.copyButtonContainer}>
          <TouchableOpacity 
            style={styles.copyButton} 
            onPress={handleCopyText}
            activeOpacity={0.7}
          >
            <Ionicons 
              name={copied ? "checkmark-circle" : "copy"} 
              size={20} 
              color={BRAND_COLORS.white} 
            />
            <Text style={styles.copyButtonText}>
              {copied ? 'Copied!' : 'Copy Prayer Text'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Prayer Text */}
        <View style={styles.prayerTextContainer}>
          <Text style={styles.prayerText}>{prayer.prayerText}</Text>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Footer Message */}
        <View style={styles.footerMessage}>
          <Ionicons name="heart" size={24} color={BRAND_COLORS.gold} />
          <Text style={styles.footerText}>May this prayer bring you peace and comfort</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: BRAND_COLORS.dark,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
  },
  loadingText: {
    fontSize: 16,
    color: BRAND_COLORS.cream,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 16,
    paddingHorizontal: 32,
  },
  errorText: {
    fontSize: 18,
    color: BRAND_COLORS.cream,
  },
  videoContainer: {
    width: '100%',
    height: 220,
    backgroundColor: '#000',
  },
  video: {
    width: '100%',
    height: 220,
  },
  prayerHeader: {
    paddingHorizontal: 24,
    paddingTop: 24,
    paddingBottom: 16,
  },
  prayerCategory: {
    fontSize: 14,
    color: BRAND_COLORS.gold,
    marginBottom: 8,
    letterSpacing: 1,
  },
  prayerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: BRAND_COLORS.cream,
    lineHeight: 36,
  },
  copyButtonContainer: {
    paddingHorizontal: 24,
    marginBottom: 24,
  },
  copyButton: {
    backgroundColor: BRAND_COLORS.burgundy,
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
  },
  copyButtonText: {
    color: BRAND_COLORS.white,
    fontSize: 16,
    fontWeight: '600',
  },
  prayerTextContainer: {
    paddingHorizontal: 24,
    paddingVertical: 16,
    backgroundColor: BRAND_COLORS.burgundy + '10',
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: BRAND_COLORS.burgundy + '30',
  },
  prayerText: {
    fontSize: 18,
    lineHeight: 32,
    color: BRAND_COLORS.cream,
    fontWeight: '400',
    letterSpacing: 0.3,
  },
  divider: {
    height: 1,
    backgroundColor: BRAND_COLORS.burgundy + '40',
    marginVertical: 24,
    marginHorizontal: 24,
  },
  footerMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    paddingHorizontal: 24,
    paddingVertical: 16,
  },
  footerText: {
    fontSize: 14,
    color: BRAND_COLORS.cream,
    fontStyle: 'italic',
    opacity: 0.8,
  },
});
