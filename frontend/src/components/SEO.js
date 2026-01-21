import { Helmet } from 'react-helmet-async';

const SEO = ({ 
  title = 'Catholic Voices & Prayers',
  description = 'Find Traditional Latin Masses, Eastern Catholic parishes, daily saints, prayers, and reverent liturgies across the United States.',
  keywords = 'Traditional Latin Mass, Catholic prayers, saints, Eastern Catholic, SSPX, FSSP, mass finder',
  image = '/og-image.png',
  url = '',
  type = 'website'
}) => {
  const siteTitle = 'Catholic Voices & Prayers';
  const fullTitle = title === siteTitle ? title : `${title} | ${siteTitle}`;
  
  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      
      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      {image && <meta property="og:image" content={image} />}
      {url && <meta property="og:url" content={url} />}
      
      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      {image && <meta name="twitter:image" content={image} />}
      
      {/* Canonical URL */}
      {url && <link rel="canonical" href={url} />}
    </Helmet>
  );
};

export default SEO;
