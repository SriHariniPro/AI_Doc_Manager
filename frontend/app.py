import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx

# API endpoint
API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="AI Document Manager", layout="wide")

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'current_doc' not in st.session_state:
    st.session_state.current_doc = None

# Sidebar
st.sidebar.title("AI Document Manager")
menu = st.sidebar.selectbox("Navigation", ["Upload", "Document Explorer", "Search", "Analytics"])

# Refresh documents list
def load_documents():
    response = requests.get(f"{API_URL}/documents")
    if response.status_code == 200:
        st.session_state.documents = response.json()["documents"]

# Upload functionality
if menu == "Upload":
    st.title("Upload New Documents")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                files = {"file": uploaded_file}
                response = requests.post(f"{API_URL}/upload", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Document processed successfully!")
                    
                    # Display document info
                    doc = result["document"]
                    st.subheader(f"Document: {doc['filename']}")
                    st.write(f"Type: {doc['type']}")
                    st.write(f"Summary: {doc['summary']}")
                    
                    # Display entities
                    if doc['metadata']['entities']:
                        st.subheader("Extracted Entities")
                        entities_df = pd.DataFrame(doc['metadata']['entities'])
                        st.dataframe(entities_df)
                    
                    # Refresh document list
                    load_documents()
                else:
                    st.error(f"Error: {response.json()['error']}")

# Document Explorer
elif menu == "Document Explorer":
    st.title("Document Explorer")
    
    # Refresh documents
    load_documents()
    
    if not st.session_state.documents:
        st.info("No documents available. Please upload some documents first.")
    else:
        # Create a dataframe for better display
        docs_simple = [{"ID": d["id"], 
                      "Filename": d["filename"], 
                      "Type": d["type"], 
                      "Summary": d["summary"]} 
                     for d in st.session_state.documents]
        docs_df = pd.DataFrame(docs_simple)
        
        st.dataframe(docs_df)
        
        if st.session_state.documents:
            doc_options = {d["id"]: d["filename"] for d in st.session_state.documents}
            
            doc_id = st.selectbox("Select document to view:", 
                                options=list(doc_options.keys()), 
                                format_func=lambda x: doc_options[x])

        
        if doc_id is not None:
            selected_doc = next(d for d in st.session_state.documents if d["id"] == doc_id)
            st.session_state.current_doc = selected_doc

            st.subheader(f"Viewing: {selected_doc['filename']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Document Type:**", selected_doc["type"])
                st.write("**Summary:**", selected_doc["summary"])
                
                # Key terms
                if selected_doc["metadata"]["key_terms"]:
                    st.write("**Key Terms:**", ", ".join(selected_doc["metadata"]["key_terms"]))
            
            with col2:
                # Display extracted dates
                if selected_doc["metadata"]["dates"]:
                    st.write("**Extracted Dates:**", ", ".join(selected_doc["metadata"]["dates"]))
                
                # Entities
                if selected_doc["metadata"]["entities"]:
                    entities_df = pd.DataFrame(selected_doc["metadata"]["entities"])
                    st.write("**Extracted Entities:**")
                    st.dataframe(entities_df)
            
            # Document text preview
            with st.expander("Document Text Preview"):
                st.text(selected_doc["text"])
            
            # Related documents
            with st.expander("Related Documents"):
                response = requests.get(f"{API_URL}/related/{doc_id}")
                if response.status_code == 200:
                    related = response.json().get("related", [])
                    if related:
                        for rel in related:
                            rel_doc = rel["document"]
                            similarity = rel["similarity"]
                            st.write(f"**{rel_doc['filename']}** (Similarity: {similarity:.2f})")
                            st.write(f"Type: {rel_doc['type']}")
                            st.write(f"Summary: {rel_doc['summary']}")
                            st.write("---")
                    else:
                        st.info("No related documents found.")

# Search functionality
elif menu == "Search":
    st.title("Semantic Document Search")
    
    query = st.text_input("Enter your search query:")
    
    if query:
        with st.spinner("Searching..."):
            response = requests.get(f"{API_URL}/search", params={"q": query})
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if results:
                    st.write(f"Found {len(results)} results:")
                    
                    for result in results:
                        doc = result["document"]
                        similarity = result["similarity"]
                        
                        st.write(f"**{doc['filename']}** (Relevance: {similarity:.2f})")
                        st.write(f"Type: {doc['type']}")
                        st.write(f"Summary: {doc['summary']}")
                        
                        with st.expander("View Details"):
                            st.write(f"**Document Text Preview:**")
                            st.text(doc["text"])
                            
                            if doc["metadata"]["entities"]:
                                st.write("**Entities:**")
                                entities_df = pd.DataFrame(doc["metadata"]["entities"])
                                st.dataframe(entities_df)
                        
                        st.write("---")
                else:
                    st.info("No matching documents found.")

# Analytics Dashboard
elif menu == "Analytics":
    st.title("Document Analytics")
    
    # Refresh documents
    load_documents()
    
    if not st.session_state.documents:
        st.info("No documents available. Please upload some documents first.")
    else:
        col1, col2 = st.columns(2)
        
        # Document type distribution
        with col1:
            st.subheader("Document Type Distribution")
            doc_types = [d["type"] for d in st.session_state.documents]
            type_counts = pd.Series(doc_types).value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index)
            st.plotly_chart(fig)
        
        # Entity type distribution
        with col2:
            st.subheader("Entity Type Distribution")
            all_entities = []
            for doc in st.session_state.documents:
                for entity in doc["metadata"]["entities"]:
                    all_entities.append(entity["type"])
            
            if all_entities:
                entity_counts = pd.Series(all_entities).value_counts()
                fig = px.bar(x=entity_counts.index, y=entity_counts.values)
                st.plotly_chart(fig)
            else:
                st.info("No entities found in documents.")
        
        # Word cloud
        st.subheader("Document Keyword Cloud")
        all_keywords = []
        for doc in st.session_state.documents:
            all_keywords.extend(doc["metadata"]["key_terms"])
        
        if all_keywords:
            # Generate word cloud
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(all_keywords))
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info("No keywords available for visualization.")
            
        # Document relationship network
        st.subheader("Document Relationship Network")
        st.write("Select a document to see relationships:")
        
        doc_options = {f"{d['id']}: {d['filename']}": d["id"] for d in st.session_state.documents}
        selected = st.selectbox("Choose document:", options=list(doc_options.keys()))
        
        if selected:
            selected_id = doc_options[selected]
            response = requests.get(f"{API_URL}/related/{selected_id}")
            
            if response.status_code == 200:
                related = response.json().get("related", [])
                
                if related:
                    # Create network graph
                    G = nx.Graph()
                    
                    # Add central node
                    central_doc = st.session_state.documents[selected_id]
                    G.add_node(central_doc["filename"], type=central_doc["type"])
                    
                    # Add related nodes
                    for rel in related:
                        rel_doc = rel["document"]
                        similarity = rel["similarity"]
                        G.add_node(rel_doc["filename"], type=rel_doc["type"])
                        G.add_edge(central_doc["filename"], rel_doc["filename"], 
                                  weight=similarity, label=f"{similarity:.2f}")
                    
                    # Visualization
                    fig, ax = plt.subplots(figsize=(10, 8))
                    
                    pos = nx.spring_layout(G)
                    
                    # Draw nodes colored by document type
                    node_colors = [0 if G.nodes[n]["type"] == central_doc["type"] else 1 
                                 for n in G.nodes()]
                    
                    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                                         node_size=500, alpha=0.8)
                    nx.draw_networkx_edges(G, pos, width=2, alpha=0.5)
                    nx.draw_networkx_labels(G, pos, font_size=8)
                    
                    # Draw edge labels
                    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
                    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
                    
                    plt.axis('off')
                    st.pyplot(fig)
                else:
                    st.info("No relationships found for this document.")

st.sidebar.markdown("---")
st.sidebar.info("This AI-powered document management system provides automated classification, semantic search, and intelligent content extraction.")