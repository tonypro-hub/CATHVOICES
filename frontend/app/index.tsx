import React from 'react';
import { View, Text, StyleSheet, Image, ScrollView, TouchableOpacity, Platform } from 'react-native';
import { Link } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';

const BRAND_COLORS = {
  burgundy: '#8B0000',
  gold: '#D4AF37',
  cream: '#F5F5DC',
  dark: '#1A1A1A',
  white: '#FFFFFF',
};

export default function Index() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Image
            source={require('../assets/images/brand/logo-white.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </View>

        {/* Hero Section */}
        <View style={styles.hero}>
          <Text style={styles.heroTitle}>Welcome to</Text>
          <Text style={styles.heroSubtitle}>Catholic Voices & Prayers</Text>
          <Text style={styles.heroDescription}>
            Discover a reverent collection of traditional Catholic prayers and devotions,
            beautifully presented with video guidance and full prayer texts.
          </Text>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsContainer}>
          <Link href="/prayers" asChild>
            <TouchableOpacity style={styles.primaryButton}>
              <Ionicons name="book" size={24} color={BRAND_COLORS.white} />
              <Text style={styles.primaryButtonText}>Explore Prayers</Text>
            </TouchableOpacity>
          </Link>

          <Link href="/about" asChild>
            <TouchableOpacity style={styles.secondaryButton}>
              <Ionicons name="information-circle-outline" size={24} color={BRAND_COLORS.burgundy} />
              <Text style={styles.secondaryButtonText}>About Us</Text>
            </TouchableOpacity>
          </Link>
        </View>

        {/* Features */}
        <View style={styles.features}>
          <View style={styles.featureCard}>
            <View style={styles.featureIconContainer}>
              <Ionicons name="videocam" size={32} color={BRAND_COLORS.gold} />
            </View>
            <Text style={styles.featureTitle}>Video Guidance</Text>
            <Text style={styles.featureDescription}>
              Watch and listen to each prayer beautifully recited
            </Text>
          </View>

          <View style={styles.featureCard}>
            <View style={styles.featureIconContainer}>
              <Ionicons name="document-text" size={32} color={BRAND_COLORS.gold} />
            </View>
            <Text style={styles.featureTitle}>Full Prayer Texts</Text>
            <Text style={styles.featureDescription}>
              Read along with large, reverent typography
            </Text>
          </View>

          <View style={styles.featureCard}>
            <View style={styles.featureIconContainer}>
              <Ionicons name="copy" size={32} color={BRAND_COLORS.gold} />
            </View>
            <Text style={styles.featureTitle}>Easy Sharing</Text>
            <Text style={styles.featureDescription}>
              Copy prayer texts to share with others
            </Text>
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerTitle}>Connect With Us</Text>
          <View style={styles.socialLinks}>
            <TouchableOpacity style={styles.socialButton}>
              <Ionicons name="logo-youtube" size={28} color={BRAND_COLORS.gold} />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton}>
              <Ionicons name="logo-instagram" size={28} color={BRAND_COLORS.gold} />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton}>
              <Ionicons name="logo-tiktok" size={28} color={BRAND_COLORS.gold} />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton}>
              <Ionicons name="logo-twitter" size={28} color={BRAND_COLORS.gold} />
            </TouchableOpacity>
            <TouchableOpacity style={styles.socialButton}>
              <Ionicons name="logo-facebook" size={28} color={BRAND_COLORS.gold} />
            </TouchableOpacity>
          </View>
          <Text style={styles.footerText}>© 2025 Catholic Voices & Prayers</Text>
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
  header: {
    alignItems: 'center',
    paddingVertical: 24,
    paddingHorizontal: 16,
    backgroundColor: BRAND_COLORS.burgundy,
  },
  logo: {
    width: 200,
    height: 80,
  },
  hero: {
    paddingHorizontal: 24,
    paddingVertical: 32,
    alignItems: 'center',
  },
  heroTitle: {
    fontSize: 18,
    color: BRAND_COLORS.gold,
    fontWeight: '500',
    marginBottom: 8,
    letterSpacing: 2,
  },
  heroSubtitle: {
    fontSize: 28,
    color: BRAND_COLORS.cream,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 16,
  },
  heroDescription: {
    fontSize: 16,
    color: BRAND_COLORS.cream,
    textAlign: 'center',
    lineHeight: 24,
    opacity: 0.9,
  },
  actionsContainer: {
    paddingHorizontal: 24,
    gap: 16,
    marginBottom: 32,
  },
  primaryButton: {
    backgroundColor: BRAND_COLORS.burgundy,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  primaryButtonText: {
    color: BRAND_COLORS.white,
    fontSize: 18,
    fontWeight: '600',
  },
  secondaryButton: {
    backgroundColor: BRAND_COLORS.cream,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  secondaryButtonText: {
    color: BRAND_COLORS.burgundy,
    fontSize: 18,
    fontWeight: '600',
  },
  features: {
    paddingHorizontal: 24,
    gap: 16,
    marginBottom: 32,
  },
  featureCard: {
    backgroundColor: BRAND_COLORS.burgundy + '20',
    borderRadius: 12,
    padding: 20,
    borderWidth: 1,
    borderColor: BRAND_COLORS.burgundy + '40',
  },
  featureIconContainer: {
    marginBottom: 12,
  },
  featureTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: BRAND_COLORS.gold,
    marginBottom: 8,
  },
  featureDescription: {
    fontSize: 14,
    color: BRAND_COLORS.cream,
    lineHeight: 20,
    opacity: 0.9,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 24,
    borderTopWidth: 1,
    borderTopColor: BRAND_COLORS.burgundy + '40',
  },
  footerTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: BRAND_COLORS.gold,
    marginBottom: 16,
  },
  socialLinks: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 16,
  },
  socialButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: BRAND_COLORS.burgundy + '40',
    alignItems: 'center',
    justifyContent: 'center',
  },
  footerText: {
    fontSize: 12,
    color: BRAND_COLORS.cream,
    opacity: 0.7,
  },
});
