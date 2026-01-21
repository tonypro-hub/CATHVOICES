import { Link } from 'react-router-dom';
import SEO from '../components/SEO';
import './SspxExplained.css';

const SspxExplained = () => {
  return (
    <div className="sspx-page" data-testid="sspx-page">
      <SEO 
        title="SSPX Explained - Sunday Obligation"
        description="A balanced explanation of the Society of St. Pius X (SSPX) and its canonical status. Learn about attending Traditional Latin Mass at SSPX chapels."
        keywords="SSPX, Society of St Pius X, Traditional Latin Mass, canonical status, Sunday obligation, Archbishop Lefebvre"
      />
      {/* Hero */}
      <section className="sspx-hero">
        <div className="container">
          <span className="sspx-label">Understanding</span>
          <h1 className="sspx-title">The SSPX & Your Sunday Obligation</h1>
          <p className="sspx-subtitle">
            A balanced explanation of the Society of St. Pius X and its canonical status
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="section sspx-content">
        <div className="container container-narrow">
          <article className="sspx-article">
            <h2>What is the SSPX?</h2>
            <p>
              The Society of St. Pius X (SSPX) is an international priestly society founded in 1970 
              by Archbishop Marcel Lefebvre. The Society was established to preserve traditional 
              Catholic practices, particularly the Traditional Latin Mass (also known as the 
              Tridentine Mass or Extraordinary Form).
            </p>
            <p>
              The SSPX operates approximately 770 churches, chapels, and Mass centers worldwide, 
              with over 700 priests serving the faithful who seek traditional Catholic worship.
            </p>

            <h2>Canonical Status</h2>
            <p>
              The canonical status of the SSPX has been a subject of discussion within the Church. 
              Here are the key points to understand:
            </p>
            
            <div className="info-box">
              <h3>Valid Sacraments</h3>
              <p>
                All sacraments celebrated by SSPX priests are <strong>valid</strong>. Their bishops 
                and priests are validly ordained, and their Masses are valid sacrifices. This has 
                been confirmed repeatedly by Rome.
              </p>
            </div>

            <div className="info-box">
              <h3>Confessions</h3>
              <p>
                In 2015, Pope Francis granted faculties to SSPX priests to validly and licitly 
                hear confessions. This was made permanent in 2017, meaning any Catholic may go to 
                an SSPX priest for confession.
              </p>
            </div>

            <div className="info-box">
              <h3>Marriages</h3>
              <p>
                In 2017, Pope Francis authorized local ordinaries (diocesan bishops) to grant 
                delegation for SSPX priests to witness marriages, thereby addressing prior 
                concerns about their validity.
              </p>
            </div>

            <h2>The Sunday Obligation</h2>
            <p>
              <strong>Yes.</strong> The Catholic Church has confirmed that attending a Mass offered by the 
              Society of St. Pius X (SSPX) can fulfill the Sunday obligation—as long as it's done without 
              rejecting the Pope or Church authority.
            </p>
            
            <div className="info-box info-box-highlight">
              <h3>Canon Law</h3>
              <p>
                <strong>Canon 1248</strong> states that the Sunday obligation is fulfilled by attending any Mass 
                celebrated "in a Catholic rite." SSPX priests use the 1962 Roman Missal—a valid Catholic 
                liturgy—and are validly ordained. The Pontifical Commission Ecclesia Dei (PCED) clarified 
                multiple times that SSPX Masses are valid, and that attendance "in the strict sense" 
                satisfies the obligation.
              </p>
            </div>
            
            <div className="quote-box">
              <blockquote>
                "The Masses they celebrate are valid... the faithful who attend these Masses do not 
                incur any sin by doing so."
              </blockquote>
              <cite>— Cardinal Castrillón Hoyos, then-President of the Pontifical Commission Ecclesia Dei (2003)</cite>
            </div>

            <h2>The SSPX's Current Status</h2>
            <p>
              The SSPX is <strong>not in schism</strong>, though it lacks official canonical status. Its priests 
              are suspended and operate without full faculties—but their sacraments are valid, including the Eucharist.
            </p>
            <ul className="bullet-list">
              <li>
                <strong>2009:</strong> Pope Benedict XVI lifted the excommunications of SSPX bishops
              </li>
              <li>
                <strong>2015–2017:</strong> Pope Francis granted SSPX priests the faculties to validly and 
                licitly hear confessions and witness marriages, highlighting pastoral concern and recognition
              </li>
            </ul>

            <h2>What About Obedience to the Bishop?</h2>
            <p>
              Bishops may discourage attending SSPX chapels, but they cannot override canon law, which permits 
              fulfilling the Sunday obligation at any valid Catholic Mass. Obedience is important—but attending 
              SSPX Mass out of sincere devotion is not rebellion if one remains united in heart and mind with 
              the Church.
            </p>

            <h2>Ongoing Reconciliation Efforts</h2>
            <p>
              The Holy See and the SSPX have been in ongoing discussions aimed at full canonical 
              regularization. Several popes have made gestures toward reconciliation:
            </p>
            <ul className="timeline-list">
              <li>
                <strong>2007:</strong> Pope Benedict XVI issued Summorum Pontificum, liberalizing 
                access to the Traditional Latin Mass for all Catholics.
              </li>
              <li>
                <strong>2009:</strong> Pope Benedict XVI remitted the excommunications of the four 
                bishops consecrated by Archbishop Lefebvre.
              </li>
              <li>
                <strong>2015-2017:</strong> Pope Francis granted permanent faculties for confessions 
                and provisions for marriages.
              </li>
              <li>
                <strong>Present:</strong> Doctrinal discussions continue between the SSPX and Rome.
              </li>
            </ul>

            <h2>Our Position</h2>
            <p>
              Catholic Voices & Prayers includes SSPX chapels in our Mass Map directory because:
            </p>
            <ul className="bullet-list">
              <li>Their Masses are valid Catholic Masses</li>
              <li>Many Catholics, especially in rural areas, have no other access to the Traditional Latin Mass</li>
              <li>Rome has granted faculties for confessions and made provisions for marriages</li>
              <li>We believe Catholics should have complete information to make informed decisions</li>
            </ul>
            <p>
              We also include all other sources of reverent Catholic liturgy: diocesan TLM communities, 
              FSSP parishes, ICKSP oratories, Ordinariate communities, and all Eastern Catholic churches.
            </p>

            <div className="disclaimer-box">
              <h3>A Note on Sedevacantism</h3>
              <p>
                Our directory does <strong>not</strong> include sedevacantist groups (such as CMRI, SSPV, 
                or independent chapels that reject the current Pope). While the SSPX is in an irregular 
                canonical situation, they remain in union with Rome and recognize the Pope as the Vicar 
                of Christ. Sedevacantist groups do not.
              </p>
            </div>
          </article>
        </div>
      </section>

      {/* CTA */}
      <section className="section sspx-cta" data-testid="sspx-cta">
        <div className="container container-narrow">
          <div className="cta-card">
            <h2>Find a Mass Near You</h2>
            <p>
              Our comprehensive Mass Map includes all forms of reverent Catholic liturgy. 
              Find a Traditional Latin Mass, Eastern Catholic parish, or reverent Novus Ordo near you.
            </p>
            <Link to="/mass-map" className="btn-primary">
              Explore the Mass Map
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SspxExplained;
