import os
import re
from typing import Annotated, Optional
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
set_llm_cache(InMemoryCache())
from langchain.cache import SQLiteCache
# set_llm_cache(SQLiteCache(database_path="Sessions/Schemas/.chatmemory.db"))

# Analyze Query with Langchain
# Assuming the existence of a function to analyze queries with Langchain

# Initialize your OpenAI API key
# openai.api_key = 'your_openai_api_key'
load_dotenv(find_dotenv(), override=True)
# print(os.environ.get("OPENAI_API_KEY"))

"""
Improving the analyze_query_with_langchain(query, description) function involves integrating more sophisticated NLP or machine learning techniques to provide real-time, context-aware feedback. One approach is to leverage OpenAI's GPT (Generative Pre-trained Transformer) models, which can understand and generate human-like text based on the input query and problem description.
"""
def analyze_query_with_langchain(userQuery, problemDescription, databaseSchema, model: Annotated[str, 'google'] = 'openai'):
    """
    Analyzes the SQL query, the problem description, and the database_schema using a GPT model
    to provide context-aware feedback and suggestions.
    """
    try:
        # Combining both query and description for comprehensive understanding
        # prompt = f"Database Schema: {database_schema}\nProblem Description: {description}\nSQL Query: {user_query}\n\nAnalyze the query and provide feedback:"

        chat_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content="You're a Chat Bot who is reponsible in helping the user who is working on problem-solving in a coding platform, where user is working in a mysql environment to write sql query. Remember you goal is to help the user in providing feedback in list of points without numbering system based on user query rather than providing solution!. Note: You are a experienced SQL Instructor and should not be wrong in giving feedback"),
                HumanMessagePromptTemplate.from_template('Database Schema: {database_schema} \nProblem Description: {problem_description}\n User SQL Query: {user_query}\n\nAnalyze the query and provide feedback:'),
            ]
        )

        """
        Task: to minimalize the database_schema rather than feeding the whole schema we will be giving the structure and first five records to understand the structure
        """
        messages = chat_template.format_messages(user_query=userQuery, problem_description=problemDescription, database_schema=databaseSchema)
        # print(messages, response)
        
        if model == 'google':
            # System Prompting
            messages = [
                SystemMessage(content="You're a Chat Bot who is reponsible in helping the user who is working on problem-solving in a coding platform, where user is working in a mysql environment to write sql query. Remember you goal is to help the user in providing feedback in list of points without numbering system based on user query rather than providing solution!. Note: You are a experienced SQL Instructor and should not be wrong in giving feedback"),
                HumanMessage(content=f'Database Schema: {databaseSchema} \nProblem Description: {problemDescription}\n User SQL Query: {userQuery}\n\nAnalyze the query and provide feedback:'),
            ]

            # Using Gemini(aka Bard) (e.g., gemini-pro) for generating the analysis
            llm = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0, convert_system_message_to_human=True) # google_api_key= '' # there is a need of behavior of using a system message
        elif model == 'openai':
            # Using ChatGPT (e.g., gpt-3.5-turbo model) for generating the analysis
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7) # api_key='
            
        response = llm.invoke(messages)

        # print(messages)
        feedback = response.content if response.content else "No feedback available."

        # Split feedback into lines, removing lines that are only whitespace or empty
        feedback = [line.strip() for line in feedback.split('\n') if line.strip()]

        # Remove leading dashes or numbers from each line
        feedback = [re.sub(r"^- |^\d+\.\s*", "", line) for line in feedback]
        # print(model, feedback)

        # Here, you can process the feedback to structure it into actionable suggestions or analysis.
        analysis = {
            "feedback": feedback,
            # You can further parse the feedback to categorize or summarize it.
        }

        return analysis

    except Exception as e:
        print(f"Error analyzing query: {e}")
        # Return a generic analysis or feedback in case of error
        return {"feedback": "Unable to analyze the query at this moment. Please try again later."}


"""
The goal of the agentic hints is to provide guidance that feels more personal and directed, encouraging the user to explore solutions while feeling supported. To accomplish this, the hints could involve suggestions for looking at the problem from different angles, asking questions to provoke thought, or gently pointing out areas that might need more attention or a different approach.

Explanation:
- Personalized Feedback: The hints are generated based on specific keywords or themes identified in the feedback. This allows the hints to be more relevant and engaging.
- Encouragement and Support: The language used in the hints aims to be supportive, offering encouragement and suggesting strategies without directly giving away the answer. This fosters a learning environment where users are motivated to discover solutions on their own.
- Actionable Suggestions: Each hint is designed to be actionable, providing clear next steps or areas for the user to explore further.
"""
# Generate Agentic Hints
def generate_agentic_hints(analysis):
    """
    Generates agentic hints based on the analysis.
    These hints are designed to be more personal and directed, encouraging exploration and understanding.
    """
    feedback = analysis.get("feedback")

    # Example of how you might categorize or structure feedback into hints
    if "incorrect" in feedback or "error" in feedback:
        return [
            "It looks like there might be a mistake in your query. Have you double-checked your syntax and table names?",
            "Try breaking down your query into smaller parts and test each part individually. This can help isolate where the problem might be.",
            "Remember, every mistake is a learning opportunity! Take a moment to review the SQL concepts related to your query."
        ]
    elif "optimization" in feedback:
        return [
            "Your query is correct, but there might be a more efficient way to achieve the same result. Have you considered using joins or subqueries?",
            "Consider indexing your tables if the query performance is critical and you're working with large datasets.",
            "Sometimes, rewriting the query or reordering conditions can lead to better performance. Experiment with different approaches."
        ]
    else:
        return [
            "Great job on constructing your query! As an additional challenge, can you modify it to achieve the same result in a different way?",
            "Consider the scalability of your query. How might it perform with a much larger dataset?",
            "Reflect on the SQL concepts you've applied here. Could any additional functions or clauses enhance your query further?"
        ]


"""
this function aims to break down the analysis or problem into smaller, logical steps. It guides the user through the thought process required to construct or debug their SQL query systematically. This method helps users understand the underlying concepts and logic, making it a powerful tool for learning and problem-solving.
The goal is to simulate a step-by-step walkthrough of how one might approach the problem or debug the query, encouraging the user to think critically and logically.

Explanation:
- Structured Approach: The function organizes the debugging or problem-solving process into a series of logical steps, guiding users to think through the problem methodically.
- Adaptive Feedback: The steps are tailored based on specific feedback or errors identified in the analysis, making the guidance relevant to the user's current challenge.
- Encouragement and Learning: By breaking down the process, users are encouraged to engage deeply with the material, fostering a deeper understanding and retention of SQL concepts.
"""
# Generate Chain of Thought
def generate_chain_of_thought(analysis):
    """
    Generates a series of logical steps or questions based on the analysis to help the user 
    approach the problem-solving process methodically.
    """
    steps = []
    feedback = analysis.get("feedback")

    # Tailor these steps based on the type of feedback or error identified in the analysis
    if "missing_join_condition" in feedback:
        steps.append("Let's start by identifying the tables we need to join.")
        steps.append("Next, determine the common column(s) between these tables for the join condition.")
        steps.append("Finally, write the JOIN statement using the common column(s) to link the tables correctly.")
    elif "aggregate_function_error" in feedback:
        steps.append("Identify the column you need to aggregate (sum, count, etc.).")
        steps.append("Consider if you need to group the results by any specific column.")
        steps.append("Write the SELECT statement including the aggregate function and GROUP BY clause if necessary.")
    elif "syntax_error" in feedback:
        steps.append("Check for common SQL syntax errors such as missing commas, quotes, or parentheses.")
        steps.append("Ensure that all keywords, function names, and operators are used correctly.")
        steps.append("Revisit the structure of your SQL statement to ensure it follows the correct order and format.")
    else:
        steps.append("Review the query to ensure it meets the requirements.")
        steps.append("Consider if there are any constraints or conditions you might have overlooked.")
        steps.append("Test each part of your query independently to ensure it works as expected.")

    # Wrap up with a general encouragement or next step
    steps.append("After revising the query based on these steps, try running it again to see if the issue has been resolved.")

    return steps

