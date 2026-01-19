import { Link } from 'react-router-dom';
import './SspxExplained.css';

const SspxExplained = () => {
  return (
    <div className="sspx-explained-page">
      {/* Hero */}
      <section className="sspx-hero">
        <div className="container">
          <h1 className="sspx-title">SSPX, Validity, and the Sunday Obligation</h1>
          <p className="sspx-subtitle">
            Understanding the Church's position on the Society of Saint Pius X
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="sspx-content">
        <div className="container container-narrow">
          
          {/* Introduction */}
          <div className="content-section">
            <p className="intro-text">
              This page provides factual information about the canonical status of the Society of 
              Saint Pius X (SSPX), the validity of their sacraments, and the conditions under which 
              attending their Masses may fulfill the Sunday obligation. This information is intended 
              to be pastoral, accurate, and informational—not directive.
            </p>
          </div>

          {/* Canonical Status */}
          <div className="content-section">
            <h2>Canonical Status of the SSPX</h2>
            <p>
              The Society of Saint Pius X exists in a <strong>canonically irregular</strong> situation 
              with respect to the Catholic Church. This means that while the SSPX is not in full 
              canonical communion with Rome, it is <strong>not considered schismatic</strong>.
            </p>
            <p>
              The SSPX was founded in 1970 by Archbishop Marcel Lefebvre. In 1988, Archbishop 
              Lefebvre consecrated four bishops without papal mandate, resulting in a declaration 
              of excommunication. However, in 2009, Pope Benedict XVI lifted the excommunications 
              of the four bishops, signaling continued dialogue between the Holy See and the Society.
            </p>
            <p>
              The Church continues to engage in dialogue with the SSPX with the hope of achieving 
              full reconciliation. Until that time, the SSPX remains in an irregular canonical 
              situation—meaning they do not have ordinary faculties from local diocesan bishops.
            </p>
          </div>

          {/* Validity of Masses and Ordinations */}
          <div className="content-section">
            <h2>Validity of SSPX Masses and Ordinations</h2>
            <p>
              The Masses celebrated by SSPX priests are <strong>valid</strong>. This is because:
            </p>
            <ul className="content-list">
              <li>
                SSPX bishops and priests are validly ordained. The episcopal consecrations, though 
                illicit (unauthorized), were valid, meaning the bishops possess true apostolic 
                succession.
              </li>
              <li>
                SSPX priests are ordained by these validly consecrated bishops, making their 
                ordinations valid as well.
              </li>
              <li>
                When a validly ordained priest celebrates Mass with proper intention and matter 
                (bread and wine), the Eucharist confected is truly the Body and Blood of Christ.
              </li>
            </ul>
            <p>
              The distinction between <em>validity</em> (whether a sacrament truly occurs) and 
              <em>liceity</em> (whether a sacrament is authorized by Church law) is important here. 
              SSPX Masses are valid but are not celebrated in full communion with the local ordinary.
            </p>
          </div>

          {/* Sunday Obligation */}
          <div className="content-section">
            <h2>Sunday Obligation and SSPX Masses</h2>
            <p>
              The question of whether attending an SSPX Mass fulfills the Sunday obligation is 
              nuanced. The Pontifical Commission <em>Ecclesia Dei</em> addressed this matter, and 
              the general guidance is as follows:
            </p>
            <ul className="content-list">
              <li>
                Because the Mass is valid, attending an SSPX Mass <strong>can</strong> fulfill the 
                Sunday obligation.
              </li>
              <li>
                However, Catholics should not attend SSPX Masses <em>habitually</em> in place of 
                Masses offered in full communion with the local bishop, as this could indicate a 
                rejection of the Pope's authority or communion with the Church.
              </li>
              <li>
                Occasional attendance for a grave reason (such as no other Mass being available, 
                travel, or particular devotion to the Traditional Latin Mass) is generally 
                considered acceptable.
              </li>
            </ul>
            <p>
              Each situation is unique, and the faithful are encouraged to consult with a trusted 
              priest or spiritual director for guidance appropriate to their circumstances.
            </p>
          </div>

          {/* Vatican Granted Faculties */}
          <div className="content-section">
            <h2>Confessions, Marriages, and Granted Faculties</h2>
            <p>
              In recent years, the Holy See has taken steps to provide for the pastoral care of 
              the faithful who attend SSPX chapels:
            </p>
            <ul className="content-list">
              <li>
                <strong>Confessions:</strong> In 2015, Pope Francis granted SSPX priests the 
                faculty to validly and licitly absolve the faithful during the Year of Mercy. 
                This faculty has been extended indefinitely, meaning confessions heard by SSPX 
                priests are both valid and licit.
              </li>
              <li>
                <strong>Marriages:</strong> In 2017, Pope Francis authorized local ordinaries to 
                grant faculties for SSPX priests to witness marriages validly and licitly, under 
                certain conditions. This provision ensures that marriages celebrated in SSPX 
                chapels can be recognized by the Church.
              </li>
            </ul>
            <p>
              These grants of faculty demonstrate the Holy See's pastoral concern for the faithful 
              who participate in SSPX communities while full reconciliation is pursued.
            </p>
          </div>

          {/* Why SSPX is Included */}
          <div className="content-section">
            <h2>Why SSPX Chapels Are Included in This Directory</h2>
            <p>
              This directory includes SSPX chapels for <strong>pastoral and informational reasons</strong>:
            </p>
            <ul className="content-list">
              <li>
                Many faithful Catholics seek reverent liturgy and may benefit from knowing the 
                location of SSPX chapels, especially where Traditional Latin Mass options are limited.
              </li>
              <li>
                The Masses celebrated at SSPX chapels are valid, and the Holy See has granted 
                faculties for confessions and marriages.
              </li>
              <li>
                Providing accurate information empowers Catholics to make informed decisions in 
                consultation with their spiritual advisors.
              </li>
            </ul>
            <p>
              This directory does not encourage or discourage attendance at any particular 
              community. It simply provides information so that the faithful may exercise prudent 
              judgment.
            </p>
          </div>

          {/* Prudence and Unity */}
          <div className="content-section">
            <h2>A Note on Prudence and Unity</h2>
            <p>
              Questions surrounding the SSPX can evoke strong feelings. Catholics of good will 
              may hold different perspectives on how best to navigate this situation.
            </p>
            <p>
              We encourage all Catholics to:
            </p>
            <ul className="content-list">
              <li>Pray for the full reconciliation of the SSPX with the Holy See.</li>
              <li>Seek guidance from trusted clergy when discerning where to attend Mass.</li>
              <li>Maintain charity and respect for those who may make different prudential judgments.</li>
              <li>Remain rooted in communion with the Pope and the universal Church.</li>
            </ul>
            <p>
              The goal of this directory is to serve the faithful by providing accurate, helpful 
              information—not to replace pastoral guidance or the formation of conscience.
            </p>
          </div>

          {/* Back Link */}
          <div className="back-section">
            <Link to="/mass-map" className="back-link">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              Return to Mass Map
            </Link>
          </div>

        </div>
      </section>
    </div>
  );
};

export default SspxExplained;
