from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_cdp_docs(base_dir: str = "./data") -> list:
    """Loads all PDFs from CDP subfolders (segment/, mparticle/, etc.)."""
    docs = []
    for platform in os.listdir(base_dir):
        platform_path = os.path.join(base_dir, platform)
        if not os.path.isdir(platform_path):
            continue
        loader = DirectoryLoader(platform_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
        docs.extend(loader.load())
    return docs

def chunk_documents(docs: list, chunk_size: int = 800, overlap: int = 100) -> list:
    """Splits docs into chunks preserving semantic boundaries."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]  # Prioritize paragraph/sentence splits
    )
    return splitter.split_documents(docs)