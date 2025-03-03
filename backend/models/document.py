import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from sentence_transformers import SentenceTransformer
import chromadb
from collections import Counter
import re

class AnalysisModel:
    def __init__(self):
        # Load NLP models
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            print("Downloading spaCy model...")
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("Downloading NLTK data...")
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('maxent_ne_chunker')
            nltk.download('words')
        
        # Initialize sentence transformer model
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB for semantic search
        self.chroma_client = chromadb.Client()
        
        # Create skills collection
        try:
            self.skills_collection = self.chroma_client.create_collection(
                name="skills",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Common technical skills
            self.common_skills = [
                "Python", "Java", "JavaScript", "C++", "SQL", "Machine Learning",
                "Data Analysis", "Project Management", "Agile", "Scrum",
                "Cloud Computing", "AWS", "Azure", "Docker", "Kubernetes",
                "React", "Angular", "Vue.js", "Node.js", "DevOps"
            ]
            
            # Add skills to ChromaDB
            self.skills_collection.add(
                documents=self.common_skills,
                ids=[f"skill_{i}" for i in range(len(self.common_skills))]
            )
        except Exception as e:
            print(f"Error initializing ChromaDB: {str(e)}")
            self.skills_collection = None

    def extract_sections(self, text):
        """Extract different sections from the resume text."""
        sections = {
            'summary': '',
            'experience': '',
            'education': '',
            'skills': '',
            'other': ''
        }
        
        # Simple section detection based on common headers
        lines = text.split('\n')
        current_section = 'other'
        
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in ['summary', 'objective', 'profile']):
                current_section = 'summary'
            elif any(keyword in line_lower for keyword in ['experience', 'work', 'employment']):
                current_section = 'experience'
            elif any(keyword in line_lower for keyword in ['education', 'academic', 'qualification']):
                current_section = 'education'
            elif any(keyword in line_lower for keyword in ['skills', 'expertise', 'competencies']):
                current_section = 'skills'
            
            sections[current_section] += line + '\n'
        
        return sections

    def analyze_structure(self, text):
        """Analyze the structure of the resume."""
        sections = self.extract_sections(text)
        
        analysis = []
        
        # Check presence and order of sections
        present_sections = [section for section, content in sections.items() if content.strip()]
        missing_sections = [section for section in sections.keys() if section not in present_sections]
        
        analysis.append(f"<h3>Section Analysis</h3>")
        analysis.append("<p><strong>Present Sections:</strong> " + ", ".join(present_sections) + "</p>")
        if missing_sections:
            analysis.append("<p><strong>Missing Sections:</strong> " + ", ".join(missing_sections) + "</p>")
        
        # Analyze section lengths
        section_lengths = {section: len(content.split()) for section, content in sections.items()}
        analysis.append("<h3>Section Lengths (word count)</h3>")
        for section, length in section_lengths.items():
            if length > 0:
                analysis.append(f"<p>{section.title()}: {length} words</p>")
        
        return analysis

    def analyze_content(self, text):
        """Analyze the content quality of the resume."""
        doc = self.nlp(text)
        sentences = sent_tokenize(text)
        
        analysis = []
        
        # Grammar and structure analysis
        analysis.append("<h3>Content Analysis</h3>")
        
        # Sentence length analysis
        sent_lengths = [len(sent.split()) for sent in sentences]
        avg_sent_length = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0
        analysis.append(f"<p><strong>Average Sentence Length:</strong> {avg_sent_length:.1f} words</p>")
        
        if avg_sent_length > 25:
            analysis.append("<p><strong>Recommendation:</strong> Consider breaking down longer sentences for better readability.</p>")
        
        # Action verbs analysis
        action_verbs = [token.text for token in doc if token.pos_ == "VERB"]
        analysis.append(f"<p><strong>Action Verbs Used:</strong> {len(set(action_verbs))}</p>")
        if action_verbs:
            analysis.append("<p><strong>Common Action Verbs:</strong> " + 
                          ", ".join(sorted(set(action_verbs))[:5]) + "</p>")
        
        return analysis

    def extract_skills(self, text):
        """Extract and analyze skills from the resume."""
        # Use NER to extract potential skill mentions
        doc = self.nlp(text)
        potential_skills = []
        
        # Extract noun phrases as potential skills
        for chunk in doc.noun_chunks:
            potential_skills.append(chunk.text)
        
        if self.skills_collection:
            # Use ChromaDB to find similar skills
            try:
                results = self.skills_collection.query(
                    query_texts=potential_skills,
                    n_results=5
                )
                
                matched_skills = []
                for matches in results['documents']:
                    matched_skills.extend(matches)
                
                return list(set(matched_skills))
            except Exception as e:
                print(f"Error querying ChromaDB: {str(e)}")
                return []
        else:
            # Fallback to simple matching
            matched_skills = []
            for skill in self.common_skills:
                if skill.lower() in text.lower():
                    matched_skills.append(skill)
            return matched_skills

    def analyze_skills(self, text, job_title):
        """Analyze skills in relation to job requirements."""
        extracted_skills = self.extract_skills(text)
        
        analysis = []
        analysis.append("<h3>Skills Analysis</h3>")
        
        if extracted_skills:
            analysis.append("<p><strong>Identified Skills:</strong></p>")
            analysis.append("<ul>")
            for skill in extracted_skills:
                analysis.append(f"<li>{skill}</li>")
            analysis.append("</ul>")
        else:
            analysis.append("<p>No specific skills were identified. Consider adding more explicit skill mentions.</p>")
        
        return analysis

    def analyze_salary_range(self, text, job_title):
        """Estimate appropriate salary range based on skills and experience."""
        analysis = []
        analysis.append("<h3>Salary Analysis</h3>")
        
        # Extract years of experience
        experience_pattern = r'(\d+)[\+]?\s*(?:years?|yrs?)'
        experience_matches = re.findall(experience_pattern, text.lower())
        years_experience = max([int(y) for y in experience_matches]) if experience_matches else 0
        
        # Count skills as a factor
        skills = self.extract_skills(text)
        skills_factor = len(skills) * 5000  # Simple multiplication factor
        
        # Basic salary calculation (very simplified)
        base_salary = 50000  # Base salary
        experience_factor = years_experience * 5000
        estimated_salary = base_salary + experience_factor + skills_factor
        
        analysis.append(f"<p><strong>Years of Experience:</strong> {years_experience}</p>")
        analysis.append(f"<p><strong>Number of Relevant Skills:</strong> {len(skills)}</p>")
        analysis.append(f"<p><strong>Estimated Salary Range:</strong> ${estimated_salary-10000:,} - ${estimated_salary+10000:,}</p>")
        
        return analysis

    def analyze_resume_sections(self, resume_text):
        """Analyze resume across different categories."""
        if not resume_text:
            return {
                "Structure Analysis": ["<p>Error: No resume content provided for analysis.</p>"],
                "Content Quality Analysis": ["<p>Error: No resume content provided for analysis.</p>"],
                "Skills & Job Fit Analysis": ["<p>Error: No resume content provided for analysis.</p>"],
                "Salary Expectation Analysis": ["<p>Error: No resume content provided for analysis.</p>"]
            }
        
        print(f"Analyzing resume with length: {len(resume_text)} characters")
        
        return {
            "Structure Analysis": self.analyze_structure(resume_text),
            "Content Quality Analysis": self.analyze_content(resume_text),
            "Skills & Job Fit Analysis": self.analyze_skills(resume_text, "Software Engineer"),
            "Salary Expectation Analysis": self.analyze_salary_range(resume_text, "Software Engineer")
        }

    def generate_full_analysis(self, resume_data, job_info, salary_expectations):
        """Generate a full analysis of the resume."""
        resume_text = resume_data.get('content', '')
        print("Starting full analysis of resume...")
        analysis_results = self.analyze_resume_sections(resume_text)
        
        return {
            "structure": analysis_results.get("Structure Analysis", []),
            "content": analysis_results.get("Content Quality Analysis", []),
            "skills_salary": {
                "skills_analysis": analysis_results.get("Skills & Job Fit Analysis", []),
                "salary_analysis": analysis_results.get("Salary Expectation Analysis", []),
                "job_info": {
                    "required_skills": self.extract_skills(resume_text),
                    "average_salary": "Based on local analysis",
                    "job_suggestions": []
                },
                "salary_expectations": salary_expectations
            }
        }
