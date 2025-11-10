import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image

st.set_page_config(page_title="PDF Page Editor", layout="wide")

st.title("📄 PDF Page Reorder / Delete / Rotate Tool")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    st.subheader("📌 Page Controls")
    updated_pages = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))  # thumbnail
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        with st.expander(f"Page {page_number + 1}"):
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(img, caption=f"Page {page_number + 1}")

            with col2:
                rotate = st.selectbox(
                    "Rotate Page",
                    [0, 90, 180, 270],
                    key=f"rotate_{page_number}"
                )
                delete = st.checkbox("Delete this page", key=f"delete_{page_number}")

            if not delete:
                updated_pages.append({"page": page_number, "rotate": rotate})

    st.subheader("🔀 Reorder Pages")
    order = st.text_input(
        "Enter new page order (comma-separated), e.g., 3,1,2",
        value=",".join(str(i+1) for i in range(len(updated_pages)))
    )

    if st.button("✅ Apply Changes & Download PDF"):
        try:
            new_doc = fitz.open()

            # Parse order
            order_list = [int(x.strip()) - 1 for x in order.split(",")]

            for idx in order_list:
                original_page_number = updated_pages[idx]["page"]
                rotate_angle = updated_pages[idx]["rotate"]

                page = doc.load_page(original_page_number)
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.show_pdf_page(page.rect, doc, original_page_number)

                if rotate_angle != 0:
                    new_page.set_rotation(rotate_angle)

            pdf_output = new_doc.write()
            new_doc.close()

            st.success("✅ PDF updated successfully!")
            st.download_button(
                label="⬇️ Download Edited PDF",
                data=pdf_output,
                file_name="edited.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
