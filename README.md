# LangGraph Tutorials & Projects

This repository contains a collection of tutorials, experiments, and projects built using LangGraph, LangChain, and related AI/ML tools.

## 📋 Overview

This repository serves as a learning resource and project showcase for:
- **LangGraph workflows** - State graphs, parallel workflows, conditional workflows, and persistence
- **AI Agents** - Multi-agent systems for various applications including manga generation
- **Chatbot implementations** - Different chatbot architectures with various features
- **Streamlit applications** - Web interfaces for AI applications

## 📁 Repository Structure

### 📓 LangGraph Tutorials
- `1_bmi_workflow.ipynb` - Basic BMI calculator workflow
- `2_simple_llm_workflow.ipynb` - Simple LLM workflow example
- `3_prompt_chaining.ipynb` - Prompt chaining techniques
- `4.ParallelWorkflow.ipynb` - Parallel workflow execution
- `5.EssayEvaluator_ParallelWorkFlow.ipynb` - Essay evaluation using parallel workflows
- `6.conditionalWorkflow.ipynb` - Conditional workflow patterns
- `7.ReviewHandling_conditionalWorkflow.ipynb` - Review handling with conditional workflows
- `8.LinkedInPost_iterative_workflow.ipynb` - LinkedIn post generation with iterative workflows
- `9.ChatBot_BasicOne.ipynb` - Basic chatbot implementation
- `10.Persistence.ipynb` - Workflow persistence techniques
- `12.langsmith.py` - LangSmith integration

### 🤖 Chatbot Implementations
- `11-ChatbotwithUI/` - Chatbot with user interface
- `11a_Chatbot_withoutStreaming/` - Chatbot without streaming
- `11b_Chatbot_withStreaming/` - Chatbot with streaming capabilities
- `11c_Chatbot_withResumeChat/` - Chatbot with chat resumption
- `11d_Chatbot_withSQLite/` - Chatbot with SQLite persistence
- `11e_Chatbot_withobservability/` - Chatbot with observability features
- `11f_Chatbot_withToolCalling/` - Chatbot with tool calling capabilities

### 🎨 Manga Generation Projects
- `Manga/` - Manga generation AI agent system
  - `agent.py` - Main agent implementation
  - `agent_base.ipynb` - Base agent notebook
  - `agent_base_human_loop.ipynb` - Agent with human-in-the-loop
  - `agent_basev2.ipynb`, `agent_basev2.py` - Improved agent versions
  - `agent_refining.ipynb` - Agent refinement techniques
  - `images_generated.ipynb` - Generated images showcase
  - `manga_workflow.py` - Manga generation workflow
  - `tables.ipynb` - Data tables for manga generation
  - `scene.txt` - Scene descriptions
  - `experiment.py`, `test.ipynb` - Experiment files
  - `Manga_backend/` - Backend for manga application
  - `New folder/` - Additional manga-related files

- `Manga_backend/` - Standalone manga backend
- `manga-streamlit-app/` - Streamlit application for manga generation

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Hyder605/LangGraph.git
cd LangGraph
```

2. Install dependencies:
```bash
pip install -r requirement.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

### Running Examples

To run a Jupyter notebook example:
```bash
jupyter notebook 1_bmi_workflow.ipynb
```

To run the manga agent:
```bash
python Manga/agent.py
```

To run the Streamlit manga app:
```bash
cd manga-streamlit-app
streamlit run app.py
```

## 🛠️ Technologies Used

- **LangGraph** - Framework for building stateful, multi-actor applications with LLMs
- **LangChain** - Framework for developing applications powered by language models
- **OpenAI API** - For accessing GPT models
- **Streamlit** - For building web applications
- **SQLite** - For data persistence
- **Jupyter Notebooks** - For interactive tutorials and experiments
- **Python** - Primary programming language

## 📚 Key Concepts Covered

### Workflow Patterns
1. **Simple Workflows** - Linear execution flows
2. **Parallel Workflows** - Concurrent task execution
3. **Conditional Workflows** - Dynamic path selection based on conditions
4. **Iterative Workflows** - Looping and refinement processes
5. **Persistent Workflows** - State preservation across sessions

### Agent Architectures
1. **Single Agent Systems** - Basic agent implementations
2. **Multi-Agent Systems** - Coordinated agent teams
3. **Human-in-the-Loop** - Interactive agent systems
4. **Tool-Calling Agents** - Agents with external tool access

### Application Domains
1. **Content Generation** - LinkedIn posts, essays, manga
2. **Chatbots** - Various chatbot implementations with different features
3. **Evaluation Systems** - Essay evaluation, review handling
4. **Creative Applications** - Manga generation with AI

## 🔧 Configuration

Most examples require API keys for LLM services. Create a `.env` file in the root directory with:

```env
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_TRACING=true
```

## 📊 Project Status

This repository is actively maintained and contains working examples of LangGraph concepts. The projects demonstrate practical applications of AI workflows and agents.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- LangGraph and LangChain teams for their amazing frameworks
- OpenAI for GPT models
- The open-source community for various libraries and tools

---

*Last Updated: December 27, 2025*