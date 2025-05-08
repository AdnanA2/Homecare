from fpdf import FPDF
import os

def export_to_pdf(text: str, filename: str):
    """
    Exports text to a PDF file.
    
    Args:
        text (str): Text to export
        filename (str): Name of the output file (without extension)
    """
    # Create PDF object
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add text
    pdf.multi_cell(0, 10, txt=text)
    
    # Ensure summaries directory exists
    os.makedirs("summaries", exist_ok=True)
    
    # Save PDF
    pdf.output(f"summaries/{filename}.pdf") 