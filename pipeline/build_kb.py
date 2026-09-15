import json
import os
from collections import defaultdict
from pipeline.ingest import load_cdp_docs, chunk_documents
from pipeline.extract import extract_from_chunk
from pipeline.standardize import standardize_extractions
from pipeline.infer import build_relationship_graph, infer_transitive_relationships

def process_platform_docs(platform: str, raw_docs: list) -> dict:
    """Processes all docs for one CDP platform into KB entries."""
    print(f"🔄 Processing {platform} documentation...")
    chunks = chunk_documents(raw_docs)
    
    all_extractions = []
    for i, chunk in enumerate(chunks):
        print(f"  → Chunk {i+1}/{len(chunks)}")
        extractions = extract_from_chunk(chunk.page_content, platform)
        standardized = standardize_extractions(extractions, platform)
        all_extractions.extend(standardized)
    
    # Build graph and infer relationships
    G = build_relationship_graph(all_extractions)
    inferred = infer_transitive_relationships(G)
    all_extractions.extend(inferred)  # Add inferred relations
    
    # Convert to KB format: group by action intent
    kb_entries = defaultdict(list)
    for item in all_extractions:
        if "action" in item and "object" in item:
            # Create a natural language question pattern from action + object
            intent = f"{item['action']} {item['object']}".strip()
            # Generate answer from subject/object/action context (simplified)
            answer = f"To {item['action']} the {item['object']}: \n" \
                     f"1. Refer to {platform} documentation for {item['object']}.\n" \
                     f"2. Use the {item['action']} method/API as described."
            kb_entries[intent].append({
                "platform": platform,
                "answer": answer.strip(),
                "source_chunk": chunk.page_content[:200] + "..."  # For debugging
            })
    
    # Deduplicate similar intents (basic fuzzy match)
    return deduplicate_kb(kb_entries)

def deduplicate_kb(kb: dict) -> dict:
    """Merge KB entries with similar intent text (e.g., 'set up source' vs 'configure source')."""
    from thefuzz import fuzz
    merged = {}
    used_intents = set()
    
    for intent, entries in kb.items():
        if intent in used_intents:
            continue
        # Find similar intents
        similar = [i for i in kb.keys() if fuzz.partial_ratio(intent, i) > 80 and i != intent]
        all_related = [intent] + similar
        
        # Merge entries from all similar intents
        merged_entries = []
        for i in all_related:
            merged_entries.extend(kb[i])
            used_intents.add(i)
        
        # Use the most frequent intent as key
        merged[intent] = merged_entries
    return merged

def build_knowledge_base():
    """Main pipeline: ingests docs → builds KB → saves to config.json."""
    print("🚀 Starting CDP Knowledge Base Pipeline...")
    raw_docs_by_platform = defaultdict(list)
    
    # 1. Load raw docs by platform
    all_docs = load_cdp_docs()
    for doc in all_docs:
        platform = doc.metadata.get("source", "").split("/")[-2]  # Assumes ./data/platform/file.pdf
        if platform in ["segment", "mparticle", "lytics", "zeotap"]:
            raw_docs_by_platform[platform].append(doc)
    
    # 2. Process each platform
    final_kb = {}
    for platform, docs in raw_docs_by_platform.items():
        if not docs:
            print(f"⚠️ No docs found for {platform}")
            continue
        platform_kb = process_platform_docs(platform, docs)
        final_kb.update(platform_kb)
    
    # 3. Save to config.json
    output_path = "./config.json"
    with open(output_path, "w") as f:
        json.dump(final_kb, f, indent=2)
    
    print(f"\n✅ Knowledge Base updated! Saved to {output_path}")
    print(f"📊 Contains {sum(len(v) for v in final_kb.values())} intents across {len(final_kb)} platforms")
    
    # 4. (Optional) Generate graph visualization
    try:
        from pipeline.visualize import save_graph_visualization
        G = build_relationship_graph(sum([v for v in final_kb.values()], []))  # Flatten extractions
        save_graph_visualization(G, "./graph.html")
        print("📈 Knowledge graph visualization saved to graph.html")
    except ImportError:
        print("💡 Install pyvis for graph visualization: pip install pyvis")

if __name__ == "__main__":
    build_knowledge_base()