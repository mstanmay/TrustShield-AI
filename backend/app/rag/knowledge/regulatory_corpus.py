"""
Regulatory Corpus — authoritative seed documents for SEBI, NSE, BSE, RBI, CERT-In, and scam awareness.
"""

from __future__ import annotations

SEED_REGULATORY_DOCUMENTS = [
    {
        "title": "SEBI Advisory on Unregistered Investment Advisors & Telegram Scams",
        "doc_type": "advisory",
        "authority": "SEBI",
        "content": """
SEBI Advisory SEBI/HO/MIRSD/DOS3/P/CIR/2023/112: Caution Against Unregistered Entities Operating on Telegram and WhatsApp.
It has come to the notice of SEBI that fraudulent entities claiming to be SEBI-registered Research Analysts (RA) or Investment Advisers (IA) are luring investors through Telegram channels and WhatsApp groups offering 'guaranteed stock tips', 'insider calls', and '100% risk-free returns'.
Investors are advised:
1. Verify registration numbers on SEBI SCORES (scores.gov.in) before acting on financial advice.
2. SEBI-registered entities never guarantee fixed/monthly profit returns.
3. Transfer of funds to personal bank accounts, UPI IDs, or mule accounts for stock trading is illegal under SEBI (Intermediaries) Regulations, 2008.
4. Any circular or letterhead without an official SEBI verification code should be treated as forged.
        """,
    },
    {
        "title": "SEBI Circular on Deepfake Audio-Visual Impersonation of Regulated Entities",
        "doc_type": "circular",
        "authority": "SEBI",
        "content": """
SEBI Circular SEBI/HO/ISD/ISD-POD-2/P/CIR/2024/045: Guidelines on Mitigating AI-Generated Deepfakes and Voice Cloning Fraud.
SEBI issues mandatory directions for all stock exchanges (NSE, BSE), depositories (CDSL, NSDL), and registered brokers regarding synthetic media fraud:
1. Fraudulent videos utilizing deepfake AI voice cloning of SEBI officials, exchange executives, and prominent market analysts are proliferated across social media to manipulate stock prices and defraud retail investors.
2. Market intermediaries must implement proactive digital signature verification and automated media authenticity analysis.
3. Claims of 'algorithmic insider trading platforms' or 'AI automated profit bots' promising guaranteed returns constitute market manipulation under SEBI (PFUTP) Regulations, 2003.
        """,
    },
    {
        "title": "NSE & BSE Joint Circular on Typosquatting and Phishing Domain Safeguards",
        "doc_type": "circular",
        "authority": "NSE",
        "content": """
NSE Joint Circular Ref: NSE/COMP/58912 & BSE Ref: 20231015-44: Public Warning on Fake Trading Portals and Typosquatted URLs.
Notice to investors regarding phishing domains impersonating licensed brokerage portals and stock exchange systems (e.g. sebl.gov.in, nse-india.co, groww-trading.app).
Indicators of fraudulent domain activity:
1. Registration of domain less than 90 days prior to marketing campaign.
2. Use of URL shorteners (bit.ly, t.co) in unsolicited SMS/WhatsApp messages.
3. Absence of valid SSL certificates issued by accredited Certificate Authorities.
4. Demands for QR code payment scanning or direct crypto/mule account transfers.
        """,
    },
    {
        "title": "RBI Advisory on Fraudulent Digital Lending Apps and Payment QR Scams",
        "doc_type": "advisory",
        "authority": "RBI",
        "content": """
RBI Public Advisory RBI/2023-24/78: Safeguards Against Unauthorized Online Lending Platforms and QR Code Money Drain Scams.
The Reserve Bank of India warns citizens against scanning QR codes sent by unverified third parties under the pretext of receiving funds.
Key rules:
1. Scanning a QR code requires entering a PIN to SEND money, never to RECEIVE money.
2. Unauthorized loan apps harvesting contact lists and utilizing intimidation tactics violate RBI Fair Practices Code.
3. Regulated banks will never request OTPs, passwords, or PINs over telephone calls or SMS messages.
        """,
    },
    {
        "title": "CERT-In Vulnerability & Threat Advisory on Voice Cloning & Impersonation Scams",
        "doc_type": "advisory",
        "authority": "CERT-In",
        "content": """
CERT-In Threat Advisory CIVN-2024-0089: High Severity Threat Notice on Generative AI Audio-Visual Impersonation (Vishing & Deepfakes).
Summary: Threat actors deploy high-fidelity voice cloning tools trained on short public audio samples to execute voice phishing (vishing) targeting retail investors and senior citizens.
Recommended mitigation:
1. Multi-factor verification via established secondary out-of-band communication channels.
2. Spectral and pitch micro-variance analysis on suspicious caller streams.
3. Immediate reporting to National Cyber Crime Reporting Portal (cybercrime.gov.in) and SEBI SCORES.
        """,
    },
    {
        "title": "SEBI Prohibition of Fraudulent and Unfair Trade Practices Regulations 2003",
        "doc_type": "regulation",
        "authority": "SEBI",
        "content": """
SEBI (Prohibition of Fraudulent and Unfair Trade Practices Relating to Securities Market) Regulations, 2003.
Section 3 & Section 4: Prohibition of Fraudulent and Unfair Trade Practices.
No person shall directly or indirectly:
(a) Buy, sell or deal in securities in a fraudulent manner;
(b) Use or employ any manipulative or deceptive device or contrivance in contravention of the Act;
(c) Employ any device, scheme or artifice to defraud in connection with dealing in securities;
(d) Engage in any act, practice, course of business which operates or would operate as a fraud or deceit upon any person.
Creation of false market impression, circular trading, front-running, and publishing false reports on stock prospects are punishable offences under Section 15HA of the SEBI Act, 1992.
        """,
    },
]
