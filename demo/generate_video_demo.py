"""
TrustShield AI — High-Definition Video Demo Generator
Creates a 1080p MP4/AVI demo video showcasing each platform view, fraud detection case,
and grievance workflow with smooth transitions and animated overlays.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
OUTPUT_VIDEO_MP4 = os.path.join(os.path.dirname(__file__), "TrustShield_AI_Platform_Demo.mp4")
OUTPUT_VIDEO_AVI = os.path.join(os.path.dirname(__file__), "TrustShield_AI_Platform_Demo.avi")

WIDTH = 1920
HEIGHT = 1080
FPS = 30
SLIDE_DURATION_SEC = 3.5
TRANSITION_DURATION_SEC = 0.8

SLIDE_FRAMES = int(SLIDE_DURATION_SEC * FPS)
TRANSITION_FRAMES = int(TRANSITION_DURATION_SEC * FPS)

SLIDES_CONFIG = [
    {
        "file": "01_landing_hero.png",
        "tag": "CASE 1: PLATFORM OVERVIEW",
        "title": "TrustShield AI — Real-Time Financial Trust Platform",
        "desc": "Autonomous oversight engine for Indian retail investors with live Financial Trust Index (98.42%)"
    },
    {
        "file": "02_landing_cta.png",
        "tag": "CASE 2: INVESTIGATION LAUNCH",
        "title": "Multi-Modal Ingestion & Investigation Entrypoint",
        "desc": "Direct access to AI forensic pipelines and regulatory intelligence verification"
    },
    {
        "file": "03_multimodal_detection.png",
        "tag": "CASE 3: MULTI-MODAL DETECTION",
        "title": "Acoustic, Video & Document Forensics Engine",
        "desc": "Video synthesis analysis (0.002ms), Voice cloning detection (94.2% acc), and Semantic OCR (1.2 TB/s)"
    },
    {
        "file": "04_feature_cards.png",
        "tag": "CASE 4: SENTINEL VIGILANCE",
        "title": "Autonomous Scam & Sentiment Analysis",
        "desc": "Continuous monitoring of social hype groups, pump-and-dump channels, and spoofed circulars"
    },
    {
        "file": "05_threat_intelligence_section.png",
        "tag": "CASE 5: THREAT INTELLIGENCE",
        "title": "Live Sensor Network & National Fraud Heatmap",
        "desc": "Real-time threat monitoring across CERT-In advisories, spoofed domains, and active incident nodes"
    },
    {
        "file": "06_analysis_nexus_graph.png",
        "tag": "CASE 6: FRAUD NETWORK GRAPH",
        "title": "Cross-Market Entity Graph & XAI Forensics",
        "desc": "Uncovering organized syndicates: Apex Capital FPI (Risk 88/100, 18 Accounts, Rs 148.5 Cr volume)"
    },
    {
        "file": "07_analysis_nexus_footer.png",
        "tag": "CASE 7: XAI FEATURE ATTRIBUTION",
        "title": "Automated Evidence Dossier Compilation",
        "desc": "Synchronized off-market order flow detection, social hype triggers, and shared IP cluster proofs"
    },
    {
        "file": "08_investigations_portal.png",
        "tag": "CASE 8: GRIEVANCE FILING",
        "title": "SEBI SCORES Grievance & Investigation Portal",
        "desc": "Structured 4-step investor redressal workflow with SLA guarantee and live registration tracking"
    },
    {
        "file": "09_grievance_wizard.png",
        "tag": "CASE 9: COMPLAINT CATEGORIZATION",
        "title": "Specialized Incident Category Classifier",
        "desc": "Broker misconduct, unauthorized Demat debits, IPO refund defaults, and social media fraud cases"
    },
    {
        "file": "10_home_overview.png",
        "tag": "CASE 10: COMPLETE ECOSYSTEM",
        "title": "Production-Ready Investor Protection Stack",
        "desc": "Unified React 19 Frontend + FastAPI Backend with end-to-end multi-agent orchestration"
    }
]

def create_slide_frame(config, index, total):
    img_path = os.path.join(SCREENSHOTS_DIR, config["file"])
    if not os.path.exists(img_path):
        canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        return canvas

    raw_img = Image.open(img_path).convert("RGBA")
    
    # Calculate scale to fit inside 1920x860 (leaving 220px for top/bottom banners)
    target_content_h = 860
    scale = min(WIDTH / raw_img.width, target_content_h / raw_img.height)
    new_w = int(raw_img.width * scale)
    new_h = int(raw_img.height * scale)
    resized_img = raw_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Create composite 1920x1080 background
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (10, 15, 13, 255))
    
    # Paste resized screenshot centered vertically between header and banner
    paste_x = (WIDTH - new_w) // 2
    paste_y = 70 + (target_content_h - new_h) // 2
    bg.paste(resized_img, (paste_x, paste_y), resized_img if resized_img.mode == 'RGBA' else None)

    draw = ImageDraw.Draw(bg)

    # Top Header Bar
    draw.rectangle([0, 0, WIDTH, 64], fill=(8, 20, 16, 245), outline=(34, 197, 94, 60), width=1)
    
    # Header Branding
    header_text = "TRUSTSHIELD AI  |  SEBI FINANCIAL TRUST & FRAUD INTELLIGENCE PLATFORM"
    draw.text((32, 20), header_text, fill=(240, 253, 244, 255))
    
    # Step indicator pill
    step_pill = f"VIEW {index + 1} OF {total}"
    draw.rectangle([WIDTH - 180, 16, WIDTH - 32, 48], fill=(34, 197, 94, 35), outline=(34, 197, 94, 180), width=1)
    draw.text((WIDTH - 165, 24), step_pill, fill=(134, 239, 172, 255))

    # Bottom Glassmorphic Overlay Banner
    banner_y = HEIGHT - 150
    draw.rectangle([0, banner_y, WIDTH, HEIGHT], fill=(6, 12, 10, 240), outline=(34, 197, 94, 50), width=1)

    # Badge Pill
    tag_x = 40
    tag_y = banner_y + 20
    tag_w = len(config["tag"]) * 9 + 24
    draw.rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + 28], fill=(34, 197, 94, 230))
    draw.text((tag_x + 12, tag_y + 6), config["tag"], fill=(0, 0, 0, 255))

    # Title & Description
    draw.text((tag_x + tag_w + 24, tag_y + 2), config["title"], fill=(240, 253, 244, 255))
    draw.text((tag_x, tag_y + 44), config["desc"], fill=(180, 195, 188, 255))

    # Progress bar line at bottom
    progress_w = int((index + 1) / total * WIDTH)
    draw.rectangle([0, HEIGHT - 6, progress_w, HEIGHT], fill=(34, 197, 94, 255))

    # Convert to BGR for OpenCV
    rgb_img = bg.convert("RGB")
    bgr_frame = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)
    return bgr_frame

def build_demo_video():
    print("Preparing slide frames...")
    frames = []
    for i, cfg in enumerate(SLIDES_CONFIG):
        frame = create_slide_frame(cfg, i, len(SLIDES_CONFIG))
        frames.append(frame)

    print(f"Loaded {len(frames)} slides. Rendering video ({WIDTH}x{HEIGHT} @ {FPS}fps)...")

    # Try MP4 codec first, fallback to AVI/MJPG
    fourcc_mp4 = cv2.VideoWriter_fourcc(*'mp4v')
    fourcc_avi = cv2.VideoWriter_fourcc(*'XVID')

    target_file = OUTPUT_VIDEO_MP4
    writer = cv2.VideoWriter(target_file, fourcc_mp4, FPS, (WIDTH, HEIGHT))
    
    if not writer.isOpened():
        print("mp4v codec not available, falling back to AVI...")
        target_file = OUTPUT_VIDEO_AVI
        writer = cv2.VideoWriter(target_file, fourcc_avi, FPS, (WIDTH, HEIGHT))

    total_slides = len(frames)
    
    for i in range(total_slides):
        current_frame = frames[i]
        next_frame = frames[(i + 1) % total_slides] if i < total_slides - 1 else None

        # Write static slide frames
        for _ in range(SLIDE_FRAMES):
            writer.write(current_frame)

        # Write cross-fade transition frames
        if next_frame is not None:
            for t in range(TRANSITION_FRAMES):
                alpha = (t + 1) / TRANSITION_FRAMES
                blended = cv2.addWeighted(next_frame, alpha, current_frame, 1.0 - alpha, 0)
                writer.write(blended)

    writer.release()
    print(f"SUCCESS: Video demo created successfully at: {target_file}")
    print(f"File size: {os.path.getsize(target_file) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    build_demo_video()
