import React from 'react';
import { Stack } from 'expo-router';

const BRAND_COLORS = {
  burgundy: '#8B0000',
  dark: '#1A1A1A',
  cream: '#F5F5DC',
};

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: BRAND_COLORS.burgundy,
        },
        headerTintColor: BRAND_COLORS.cream,
        headerTitleStyle: {
          fontWeight: '600',
        },
        contentStyle: {
          backgroundColor: BRAND_COLORS.dark,
        },
      }}
    >
      <Stack.Screen 
        name="index" 
        options={{ 
          headerShown: false 
        }} 
      />
      <Stack.Screen 
        name="prayers/index" 
        options={{ 
          title: 'Prayers',
        }} 
      />
      <Stack.Screen 
        name="prayers/[id]" 
        options={{ 
          title: 'Prayer',
        }} 
      />
      <Stack.Screen 
        name="about" 
        options={{ 
          title: 'About Us',
        }} 
      />
    </Stack>
  );
}
