import streamlit as st
import cv2
import numpy as np
import os
import tempfile
from PIL import Image
from utils import aadhaar_verification, pan_verification, helpers
import re

# Set page config
st.set_page_config(
    page_title="Aadhaar/PAN Verifier",
    page_icon="🆔",
    layout="wide"
)

# Page header
st.title("🇮🇳 Aadhaar & PAN Verification System")
st.subheader("HyperVerge-style Fraud Detection for Indian Identity Documents")
st.markdown("---")

# Tab interface
tab1, tab2 = st.tabs(["Aadhaar Verification", "PAN Verification"])

with tab1:
    st.header("Aadhaar Card Verification")
    uploaded_aadhaar = st.file_uploader(
        "Upload Aadhaar Card", 
        type=["jpg", "png", "jpeg"],
        help="Upload front side of Aadhaar card"
    )
    
    if uploaded_aadhaar:
        aadhaar_img = Image.open(uploaded_aadhaar)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(aadhaar_img, caption="Uploaded Aadhaar", use_column_width=True)
        
        with col2:
            st.subheader("Verification Report")
            with st.spinner("Analyzing Aadhaar security features..."):
                # Convert to OpenCV format
                image_np = np.array(aadhaar_img)
                image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                
                # Run verification checks
                results = aadhaar_verification.verify(image_cv)
                
                # Display results
                col_a1, col_a2, col_a3 = st.columns(3)
                
                with col_a1:
                    st.metric("Document Structure", 
                              value="VALID" if results['structure_valid'] else "INVALID",
                              delta=None if results['structure_valid'] else "Format Issue")
                
                with col_a2:
                    st.metric("Photo Integrity", 
                              value="CLEAN" if results['photo_tamper_score'] < 30 else "TAMPERED",
                              delta=f"{results['photo_tamper_score']}%")
                
                with col_a3:
                    st.metric("Text Validation", 
                              value="VALID" if results['text_valid'] else "INVALID",
                              delta=None if results['text_valid'] else "OCR Issue")
                
                # Fraud score calculation
                fraud_score = 0
                if not results['structure_valid']: fraud_score += 40
                if results['photo_tamper_score'] >= 30: fraud_score += 30
                if not results['text_valid']: fraud_score += 30
                
                st.progress(fraud_score/100, text=f"Fraud Probability: {fraud_score}%")
                
                if fraud_score > 70:
                    st.error("🚨 HIGH FRAUD RISK: Multiple security issues detected!")
                elif fraud_score > 40:
                    st.warning("⚠️ MEDIUM RISK: Potential document issues found")
                else:
                    st.success("✅ LOW RISK: Document appears authentic")
                
                # Show extracted text
                with st.expander("Extracted Information"):
                    st.json(results['extracted_text'])

with tab2:
    st.header("PAN Card Verification")
    uploaded_pan = st.file_uploader(
        "Upload PAN Card", 
        type=["jpg", "png", "jpeg"],
        help="Upload PAN card image"
    )
    
    if uploaded_pan:
        pan_img = Image.open(uploaded_pan)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(pan_img, caption="Uploaded PAN", use_column_width=True)
        
        with col2:
            st.subheader("Verification Report")
            with st.spinner("Analyzing PAN security features..."):
                # Convert to OpenCV format
                image_np = np.array(pan_img)
                image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                
                # Run verification checks
                results = pan_verification.verify(image_cv)
                
                # Display results
                col_p1, col_p2, col_p3 = st.columns(3)
                
                with col_p1:
                    st.metric("Tampering Detection", 
                              value="CLEAN" if results['tamper_score'] < 25 else "TAMPERED",
                              delta=f"{results['tamper_score']}%")
                
                with col_p2:
                    st.metric("Hologram Check", 
                              value="PRESENT" if results['hologram_detected'] else "ABSENT",
                              delta=None if results['hologram_detected'] else "Suspicious")
                
                with col_p3:
                    st.metric("PAN Format", 
                              value="VALID" if results['pan_valid'] else "INVALID",
                              delta=None if results['pan_valid'] else "Format Issue")
                
                # Fraud score calculation
                fraud_score = 0
                if results['tamper_score'] >= 25: fraud_score += 40
                if not results['hologram_detected']: fraud_score += 30
                if not results['pan_valid']: fraud_score += 30
                
                st.progress(fraud_score/100, text=f"Fraud Probability: {fraud_score}%")
                
                if fraud_score > 70:
                    st.error("🚨 HIGH FRAUD RISK: Document likely forged!")
                elif fraud_score > 40:
                    st.warning("⚠️ MEDIUM RISK: Potential document issues")
                else:
                    st.success("✅ LOW RISK: Document appears authentic")
                
                # Show extracted text
                with st.expander("Extracted Information"):
                    st.json(results['extracted_text'])

# Footer
st.markdown("---")
st.subheader("About This System")
st.markdown("""
**Key Technologies:**
- Aadhaar/PAN Structure Validation
- Document Tampering Detection
- OCR Information Extraction
- Security Feature Analysis

**Dataset Compatibility:**
- Works with Kaggle Aadhaar/PAN datasets
- Handles real and tampered documents
- Processes various image qualities
""")
st.caption("Note: This demo uses computer vision techniques for educational purposes | Not for real identity verification")
