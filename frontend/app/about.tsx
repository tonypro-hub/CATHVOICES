import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

const BRAND_COLORS = {
  burgundy: '#8B0000',
  gold: '#D4AF37',
  cream: '#F5F5DC',
  dark: '#1A1A1A',
  white: '#FFFFFF',
};

const SOCIAL_LINKS = {
  youtube: 'https://www.youtube.com/@CatholicVoicesPrayers',
  instagram: 'https://www.instagram.com/catholic_voices/',
  tiktok: 'https://www.tiktok.com/@catholicvoicesprayers',
  twitter: 'https://x.com/CatholicVoices1',
  facebook: 'https://www.facebook.com/p/Catholic-Voices-Prayers-61558676517811/',
};

export default function AboutScreen() {
  const openLink = async (url: string) => {
    try {
      const supported = await Linking.canOpenURL(url);
      if (supported) {
        await Linking.openURL(url);
      }
    } catch (error) {
      console.error('Error opening link:', error);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        {/* Logo */}
        <View style={styles.logoContainer}>
          <Image
            source={require('../assets/images/brand/logo-white.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </View>

        {/* Mission */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Our Mission</Text>
          <Text style={styles.bodyText}>
            Catholic Voices & Prayers is dedicated to bringing the beauty and richness of 
            traditional Catholic prayers to the faithful around the world. Through our 
            carefully crafted videos and devotional resources, we aim to help you deepen 
            your prayer life and grow closer to God.
          </Text>
        </View>

        {/* About */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>What We Offer</Text>
          <View style={styles.featuresList}>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={24} color={BRAND_COLORS.gold} />
              <Text style={styles.featureText}>Traditional Catholic prayers with video guidance</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={24} color={BRAND_COLORS.gold} />
              <Text style={styles.featureText}>Full prayer texts in beautiful, readable format</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={24} color={BRAND_COLORS.gold} />
              <Text style={styles.featureText}>Easy access to share and copy prayers</Text>
            </View>
            <View style={styles.featureItem}>
              <Ionicons name="checkmark-circle" size={24} color={BRAND_COLORS.gold} />
              <Text style={styles.featureText}>Regular updates with new prayers and content</Text>
            </View>
          </View>
        </View>

        {/* Social Media */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Connect With Us</Text>
          <Text style={styles.bodyText}>
            Follow us on social media to stay updated with new prayers, devotional content, 
            and join our growing community of faithful Catholics.
          </Text>
          
          <View style={styles.socialContainer}>
            <TouchableOpacity 
              style={styles.socialCard}
              onPress={() => openLink(SOCIAL_LINKS.youtube)}
            >
              <Ionicons name="logo-youtube" size={32} color={BRAND_COLORS.gold} />
              <Text style={styles.socialLabel}>YouTube</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.socialCard}
              onPress={() => openLink(SOCIAL_LINKS.instagram)}
            >
              <Ionicons name="logo-instagram" size={32} color={BRAND_COLORS.gold} />
              <Text style={styles.socialLabel}>Instagram</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.socialCard}
              onPress={() => openLink(SOCIAL_LINKS.tiktok)}
            >
              <Ionicons name="logo-tiktok" size={32} color={BRAND_COLORS.gold} />
              <Text style={styles.socialLabel}>TikTok</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.socialCard}
              onPress={() => openLink(SOCIAL_LINKS.twitter)}
            >
              <Ionicons name="logo-twitter" size={32} color={BRAND_COLORS.gold} />
              <Text style={styles.socialLabel}>Twitter/X</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.socialCard}
              onPress={() => openLink(SOCIAL_LINKS.facebook)}
            >
              <Ionicons name="logo-facebook" size={32} color={BRAND_COLORS.gold} />
              <Text style={styles.socialLabel}>Facebook</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <View style={styles.crossIcon}>
            <Text style={styles.crossText}>✝</Text>
          </View>
          <Text style={styles.footerText}>© 2025 Catholic Voices & Prayers</Text>
          <Text style={styles.footerSubtext}>May God bless you</Text>
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
  logoContainer: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: BRAND_COLORS.burgundy + '20',
  },
  logo: {
    width: 180,
    height: 80,
  },
  section: {
    paddingHorizontal: 24,
    paddingVertical: 24,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: BRAND_COLORS.gold,
    marginBottom: 16,
  },
  bodyText: {
    fontSize: 16,
    lineHeight: 26,
    color: BRAND_COLORS.cream,
    opacity: 0.95,
  },
  featuresList: {
    gap: 16,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  featureText: {
    flex: 1,
    fontSize: 16,
    lineHeight: 24,
    color: BRAND_COLORS.cream,
    opacity: 0.95,
  },
  socialContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 16,
  },
  socialCard: {
    width: '30%',
    aspectRatio: 1,
    backgroundColor: BRAND_COLORS.burgundy + '20',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: BRAND_COLORS.burgundy + '40',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  socialLabel: {
    fontSize: 12,
    color: BRAND_COLORS.cream,
    fontWeight: '500',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 24,
    gap: 8,
  },
  crossIcon: {
    marginBottom: 8,
  },
  crossText: {
    fontSize: 32,
    color: BRAND_COLORS.gold,
  },
  footerText: {
    fontSize: 14,
    color: BRAND_COLORS.cream,
    opacity: 0.8,
  },
  footerSubtext: {
    fontSize: 14,
    color: BRAND_COLORS.gold,
    fontStyle: 'italic',
  },
});
