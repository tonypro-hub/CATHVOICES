/**
 * PRODUCT DATA FILE
 * ===================
 * All store products are managed here for easy updates.
 * 
 * TO ADD A PRODUCT:
 * 1. Add a new object to the appropriate category array
 * 2. Include: id, name, description, image, affiliateUrl, affiliateNetwork
 * 
 * TO CHANGE AFFILIATE NETWORK:
 * 1. Update the affiliateUrl for the product
 * 2. Update affiliateNetwork field (for tracking purposes)
 * 
 * SUPPORTED AFFILIATE NETWORKS:
 * - amazon (Amazon Associates)
 * - catholiccompany (The Catholic Company)
 * - tanbooks (TAN Books)
 * - ewtn (EWTN Religious Catalogue)
 * - custom (Direct publisher/vendor links)
 */

export interface Product {
  id: string;
  name: string;
  description: string;
  image: string;
  affiliateUrl: string;
  affiliateNetwork: 'amazon' | 'catholiccompany' | 'tanbooks' | 'ewtn' | 'custom';
  price?: string; // Optional display price
}

export interface Category {
  id: string;
  name: string;
  description: string;
  icon: string; // SVG path or icon identifier
  products: Product[];
}

// Placeholder image for products without images
const PLACEHOLDER_IMAGE = 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80';

export const storeCategories: Category[] = [
  {
    id: 'catholic-books',
    name: 'Catholic Books',
    description: 'Timeless works of Catholic spirituality, theology, and devotion',
    icon: 'book',
    products: [
      {
        id: 'intro-devout-life',
        name: 'Introduction to the Devout Life',
        description: 'St. Francis de Sales\' classic guide to growing in holiness through everyday life. A timeless masterpiece of spiritual direction.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Introduction-Devout-Life-Francis-Sales/dp/0679651039?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$12.99'
      },
      {
        id: 'imitation-christ',
        name: 'The Imitation of Christ',
        description: 'Thomas à Kempis\' profound meditation on the spiritual life, second only to the Bible in Christian readership.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Imitation-Christ-Thomas-Kempis/dp/0486431185?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$6.99'
      },
      {
        id: 'story-soul',
        name: 'Story of a Soul',
        description: 'The autobiography of St. Thérèse of Lisieux, revealing her "Little Way" of spiritual childhood and trust in God.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Story-Soul-Autobiography-Therese-Lisieux/dp/0895551551?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$14.95'
      },
      {
        id: 'confessions-augustine',
        name: 'Confessions of St. Augustine',
        description: 'One of the most influential works in Christian literature—Augustine\'s journey from sin to salvation.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Confessions-Saint-Augustine-dp-0385029551/dp/0385029551?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$15.00'
      },
      {
        id: 'true-devotion-mary',
        name: 'True Devotion to Mary',
        description: 'St. Louis de Montfort\'s profound explanation of Marian consecration and its role in our spiritual life.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/True-Devotion-Mary-Louis-Montfort/dp/0895551543?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$12.95'
      },
      {
        id: 'interior-castle',
        name: 'Interior Castle',
        description: 'St. Teresa of Ávila\'s masterwork on prayer and the soul\'s journey toward union with God.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Interior-Castle-Teresa-Avila/dp/0385036434?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$14.00'
      }
    ]
  },
  {
    id: 'rosaries',
    name: 'Rosaries',
    description: 'Beautiful rosaries crafted for prayer and devotion',
    icon: 'rosary',
    products: [
      {
        id: 'olive-wood-rosary',
        name: 'Olive Wood Rosary from Bethlehem',
        description: 'Handcrafted rosary made from genuine olive wood from the Holy Land. Each bead is unique.',
        image: 'https://images.unsplash.com/photo-1609234656388-0ff363383899?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B07VQJX5KZ?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$18.99'
      },
      {
        id: 'combat-rosary',
        name: 'WWI Combat Rosary',
        description: 'Replica of the original combat rosary designed for soldiers. Durable construction with pull-chain design.',
        image: 'https://images.unsplash.com/photo-1609234656388-0ff363383899?w=400&q=80',
        affiliateUrl: 'https://www.romancatholicgear.com/combat-rosary?ref=catholicvoices',
        affiliateNetwork: 'custom',
        price: '$34.95'
      },
      {
        id: 'crystal-rosary',
        name: 'Aurora Borealis Crystal Rosary',
        description: 'Elegant crystal rosary with aurora borealis finish. Comes in a protective case.',
        image: 'https://images.unsplash.com/photo-1609234656388-0ff363383899?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B003XWJMK8?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$24.99'
      },
      {
        id: 'cord-rosary',
        name: 'Knotted Cord Rosary',
        description: 'Traditional knotted cord rosary, durable and perfect for travel. Handmade with care.',
        image: 'https://images.unsplash.com/photo-1609234656388-0ff363383899?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B00K7FXJFQ?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$8.99'
      }
    ]
  },
  {
    id: 'prayer-cards',
    name: 'Prayer Cards',
    description: 'Portable prayer cards for daily devotion and meditation',
    icon: 'card',
    products: [
      {
        id: 'divine-mercy-card',
        name: 'Divine Mercy Prayer Card',
        description: 'Laminated prayer card featuring the Divine Mercy image and chaplet prayers.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B001GXRDJ2?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$2.99'
      },
      {
        id: 'st-michael-card',
        name: 'St. Michael Prayer Card',
        description: 'The powerful St. Michael the Archangel prayer on a durable laminated card.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B001E6OYT4?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$2.49'
      },
      {
        id: 'holy-cards-set',
        name: 'Assorted Holy Cards (100 pack)',
        description: 'Collection of 100 assorted holy cards featuring various saints and prayers.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B07D3BHYRR?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$19.99'
      },
      {
        id: 'memorare-card',
        name: 'Memorare Prayer Card',
        description: 'Beautiful card with the Memorare prayer to the Blessed Virgin Mary.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B00KBPXR5C?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$2.99'
      }
    ]
  },
  {
    id: 'devotionals',
    name: 'Devotionals',
    description: 'Daily devotionals and prayer guides for spiritual growth',
    icon: 'devotional',
    products: [
      {
        id: 'daily-roman-missal',
        name: 'Daily Roman Missal',
        description: 'Complete missal with all Sunday and daily Mass readings. Essential for following the liturgy.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Daily-Roman-Missal-Burgundy-Bonded/dp/1936045567?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$59.95'
      },
      {
        id: 'magnificat',
        name: 'Magnificat Monthly Missal',
        description: 'Monthly publication with daily Mass texts, prayers, and spiritual readings.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://us.magnificat.net/subscription?ref=catholicvoices',
        affiliateNetwork: 'custom',
        price: '$4.99/month'
      },
      {
        id: 'divine-office',
        name: 'Christian Prayer: Liturgy of the Hours',
        description: 'One-volume edition of the Liturgy of the Hours for morning and evening prayer.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Christian-Prayer-Liturgy-Hours/dp/0899424066?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$29.95'
      },
      {
        id: 'pieta-prayer-book',
        name: 'Pieta Prayer Book',
        description: 'Popular collection of traditional Catholic prayers, novenas, and devotions.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Pieta-Prayer-Book-Large-Print/dp/B002ACPLEO?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$7.95'
      },
      {
        id: 'manual-prayers',
        name: 'Manual of Prayers',
        description: 'The official prayer book of the Knights of Columbus, containing traditional prayers and devotions.',
        image: 'https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/Manual-Prayers-Knights-Columbus/dp/1936045265?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$24.95'
      }
    ]
  },
  {
    id: 'religious-gifts',
    name: 'Religious Gifts',
    description: 'Meaningful gifts to inspire faith and devotion',
    icon: 'gift',
    products: [
      {
        id: 'crucifix-wall',
        name: 'Wooden Wall Crucifix',
        description: 'Traditional wooden crucifix for home display. Hand-painted corpus.',
        image: 'https://images.unsplash.com/photo-1508186736123-44a5fcb36f9f?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B07BGRVZMT?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$32.99'
      },
      {
        id: 'sacred-heart-statue',
        name: 'Sacred Heart of Jesus Statue',
        description: 'Hand-painted resin statue of the Sacred Heart, 8 inches tall.',
        image: 'https://images.unsplash.com/photo-1508186736123-44a5fcb36f9f?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B001AFRX40?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$29.99'
      },
      {
        id: 'miraculous-medal',
        name: 'Miraculous Medal Necklace',
        description: 'Sterling silver Miraculous Medal on 18-inch chain. A beautiful expression of Marian devotion.',
        image: 'https://images.unsplash.com/photo-1609234656388-0ff363383899?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B0013G4BJU?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$39.95'
      },
      {
        id: 'holy-water-font',
        name: 'Holy Water Font',
        description: 'Ceramic holy water font for home entryway. Features Madonna and Child.',
        image: 'https://images.unsplash.com/photo-1508186736123-44a5fcb36f9f?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B001E6N4AC?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$16.99'
      },
      {
        id: 'st-benedict-medal',
        name: 'St. Benedict Medal',
        description: 'Traditional St. Benedict medal for protection. Bronze finish with cord.',
        image: 'https://images.unsplash.com/photo-1609234656388-0ff363383899?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B07KPNJ7JY?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$12.99'
      },
      {
        id: 'first-communion-set',
        name: 'First Communion Gift Set',
        description: 'Complete set including rosary, prayer book, and medal. Perfect for the special occasion.',
        image: 'https://images.unsplash.com/photo-1508186736123-44a5fcb36f9f?w=400&q=80',
        affiliateUrl: 'https://www.amazon.com/dp/B07NDJTCML?tag=catholicvoices-20',
        affiliateNetwork: 'amazon',
        price: '$34.95'
      }
    ]
  }
];

// Helper function to get all products
export const getAllProducts = (): Product[] => {
  return storeCategories.flatMap(category => category.products);
};

// Helper function to get category by ID
export const getCategoryById = (id: string): Category | undefined => {
  return storeCategories.find(category => category.id === id);
};

// Helper function to get product by ID
export const getProductById = (id: string): Product | undefined => {
  return getAllProducts().find(product => product.id === id);
};

// Affiliate disclosure text
export const AFFILIATE_DISCLOSURE = `As an Amazon Associate and affiliate of other retailers, Catholic Voices & Prayers earns from qualifying purchases. This helps support our ministry at no additional cost to you. We only recommend products we believe will support your faith journey.`;

export const AFFILIATE_DISCLOSURE_SHORT = `Affiliate links help support our ministry at no cost to you.`;
