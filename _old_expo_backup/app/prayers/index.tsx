import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import { Link } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

const BRAND_COLORS = {
  burgundy: '#8B0000',
  gold: '#D4AF37',
  cream: '#F5F5DC',
  dark: '#1A1A1A',
  white: '#FFFFFF',
};

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Prayer {
  id: string;
  title: string;
  videoId: string;
  prayerText: string;
  category: string;
  createdAt: string;
}

export default function PrayersListScreen() {
  const [prayers, setPrayers] = useState<Prayer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPrayers();
  }, []);

  const fetchPrayers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/api/prayers`);
      setPrayers(response.data);
    } catch (error) {
      console.error('Error fetching prayers:', error);
      Alert.alert('Error', 'Failed to load prayers. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={BRAND_COLORS.gold} />
          <Text style={styles.loadingText}>Loading prayers...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (prayers.length === 0) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.emptyContainer}>
          <Ionicons name="book-outline" size={64} color={BRAND_COLORS.gold} />
          <Text style={styles.emptyTitle}>No Prayers Yet</Text>
          <Text style={styles.emptyDescription}>
            Prayers will appear here once they are added.
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Traditional Catholic Prayers</Text>
          <Text style={styles.headerSubtitle}>
            Select a prayer to watch and read along
          </Text>
        </View>

        <View style={styles.prayersContainer}>
          {prayers.map((prayer) => (
            <Link key={prayer.id} href={`/prayers/${prayer.id}`} asChild>
              <TouchableOpacity style={styles.prayerCard}>
                <View style={styles.prayerCardContent}>
                  <View style={styles.iconContainer}>
                    <Ionicons name="videocam" size={24} color={BRAND_COLORS.gold} />
                  </View>
                  <View style={styles.prayerInfo}>
                    <Text style={styles.prayerTitle}>{prayer.title}</Text>
                    <Text style={styles.prayerCategory}>{prayer.category}</Text>
                  </View>
                  <Ionicons name="chevron-forward" size={24} color={BRAND_COLORS.gold} />
                </View>
              </TouchableOpacity>
            </Link>
          ))}
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    gap: 16,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: BRAND_COLORS.cream,
  },
  emptyDescription: {
    fontSize: 16,
    color: BRAND_COLORS.cream,
    textAlign: 'center',
    opacity: 0.8,
  },
  header: {
    paddingHorizontal: 24,
    paddingVertical: 24,
    backgroundColor: BRAND_COLORS.burgundy + '20',
    borderBottomWidth: 1,
    borderBottomColor: BRAND_COLORS.burgundy + '40',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: BRAND_COLORS.gold,
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 14,
    color: BRAND_COLORS.cream,
    opacity: 0.9,
  },
  prayersContainer: {
    paddingHorizontal: 16,
    paddingTop: 16,
    gap: 12,
  },
  prayerCard: {
    backgroundColor: BRAND_COLORS.burgundy + '20',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: BRAND_COLORS.burgundy + '40',
    overflow: 'hidden',
  },
  prayerCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    gap: 12,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: BRAND_COLORS.burgundy + '40',
    alignItems: 'center',
    justifyContent: 'center',
  },
  prayerInfo: {
    flex: 1,
  },
  prayerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: BRAND_COLORS.cream,
    marginBottom: 4,
  },
  prayerCategory: {
    fontSize: 14,
    color: BRAND_COLORS.gold,
  },
});
