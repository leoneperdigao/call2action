"""AI-powered summarization and call-to-action generation using LangChain."""

from typing import List

from langchain.docstore.document import Document
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from call2action.config import Settings


class Summarizer:
    """Generates summaries and call-to-actions using LangChain and OpenAI GPT models."""

    def __init__(self, settings: Settings):
        """Initialize the summarizer with OpenAI configuration."""
        self.settings = settings
        
        # Initialize LangChain ChatOpenAI model
        llm_params = {
            "model": settings.openai_model,
            "api_key": settings.openai_api_key,
            "max_tokens": 4096,  # Increased for summaries - need more tokens for output
        }
        
        # Only add temperature if not default (1.0) - some models don't support custom values
        if settings.openai_temperature != 1.0:
            llm_params["temperature"] = settings.openai_temperature
        
        self.llm = ChatOpenAI(**llm_params)
        
        # Initialize text splitter for chunking long documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,  # Reasonable chunk size for context
            chunk_overlap=200,  # Small overlap to maintain context
            length_function=len,
        )
        
        print(f"✅ LangChain summarizer initialized (model: {settings.openai_model})")

    def generate_summary(self, transcript: str) -> str:
        """
        Generate a comprehensive summary using LangChain's native parallel processing.
        
        This implementation:
        - Splits transcript into chunks
        - Summarizes chunks in PARALLEL using RunnableParallel
        - Combines summaries into final comprehensive summary
        - Shows real-time progress

        Args:
            transcript: The full transcript text

        Returns:
            A summary of the transcript
        """
        print("📝 Generating summary with parallel chunk processing...")
        
        # Split transcript into chunks
        texts = self.text_splitter.split_text(transcript)
        docs = [Document(page_content=t) for t in texts]
        
        print(f"   📄 Split transcript into {len(docs)} chunks")
        print("   🔄 Summarizing chunks in parallel...")
        
        # Custom prompt for chunk summarization
        chunk_prompt_template = ChatPromptTemplate.from_template(
            """You are an expert at summarizing technical software development meetings.

Write a comprehensive and detailed summary of the following meeting transcript segment IN ENGLISH.
Even if the transcript is in another language, your summary MUST be in English.

This is a technical discussion about software development, so include:
- Technical terms, architecture decisions, and implementation details
- Specific technologies, tools, frameworks, or systems mentioned
- Problems discussed and proposed solutions
- Design decisions and their rationale
- Performance, scalability, or maintenance concerns
- Team structure and responsibilities
- Timeline or prioritization discussions

Be thorough and technical - don't oversimplify.
IMPORTANT: Write the entire summary in English, regardless of the transcript language.

Transcript Segment:
{text}

DETAILED SUMMARY (IN ENGLISH):"""
        )
        
        # Create a summarization chain for a single chunk
        chunk_chain = chunk_prompt_template | self.llm
        
        # Summarize chunks in parallel using batch processing
        chunk_summaries = []
        
        print("   🔄 Processing chunks in parallel...")
        
        # Prepare inputs for batch processing
        batch_inputs = [{"text": doc.page_content} for doc in docs]
        
        try:
            # Use batch() for parallel processing - LangChain's native way
            # This automatically handles parallel execution efficiently
            results = chunk_chain.batch(batch_inputs)
            
            # Extract summaries from results with error handling
            for i, result in enumerate(results):
                try:
                    summary_text = result.content.strip()
                    if len(summary_text) == 0:
                        print(f"   ⚠️  Chunk {i+1}/{len(results)}: Empty response, retrying...")
                        # Retry this specific chunk
                        retry_result = chunk_chain.invoke({"text": docs[i].page_content})
                        summary_text = retry_result.content.strip()
                        if len(summary_text) == 0:
                            print(f"   ❌ Chunk {i+1}/{len(results)}: Failed after retry, using placeholder")
                            summary_text = f"[Chunk {i+1} summarization failed - content unavailable]"
                    print(f"   ✓ Chunk {i+1}/{len(results)}: {len(summary_text)} chars")
                    chunk_summaries.append(summary_text)
                except Exception as chunk_error:
                    print(f"   ❌ Chunk {i+1}/{len(results)}: Error - {chunk_error}")
                    # Add placeholder for failed chunk to maintain order
                    chunk_summaries.append(f"[Chunk {i+1} summarization failed: {str(chunk_error)}]")
                    
        except Exception as e:
            print(f"   ⚠️  Error during parallel summarization: {e}")
            # Fallback to sequential processing if parallel fails
            print("   🔄 Falling back to sequential processing...")
            for i, doc in enumerate(docs):
                try:
                    response = chunk_chain.invoke({"text": doc.page_content})
                    summary_text = response.content.strip()
                    if len(summary_text) > 0:
                        chunk_summaries.append(summary_text)
                        print(f"   ✓ Chunk {i+1}/{len(docs)}: {len(summary_text)} chars")
                    else:
                        print(f"   ❌ Chunk {i+1}/{len(docs)}: Empty response")
                        chunk_summaries.append(f"[Chunk {i+1} summarization failed - empty response]")
                except Exception as chunk_error:
                    print(f"   ❌ Chunk {i+1}/{len(docs)}: {chunk_error}")
                    chunk_summaries.append(f"[Chunk {i+1} summarization failed: {str(chunk_error)}]")
        
        print("   🔗 Combining chunk summaries...")
        
        # Debug: Check chunk summaries
        print(f"   📊 Total chunks to combine: {len(chunk_summaries)}")
        total_chars = sum(len(s) for s in chunk_summaries)
        print(f"   📏 Total characters in all chunks: {total_chars}")
        
        if not chunk_summaries or total_chars == 0:
            print("   ⚠️  ERROR: No chunk summaries to combine!")
            return ""
        
        # For large documents, use hierarchical summarization:
        # Group chunks -> create intermediate summaries -> final summary
        if len(chunk_summaries) > 10 or total_chars > 100000:
            print(f"   🔄 Large document ({len(chunk_summaries)} chunks, {total_chars} chars)")
            print(f"   📦 Using hierarchical summarization (group chunks -> combine)")
            
            # Group chunks into batches of 6 for intermediate summaries
            group_size = 6
            intermediate_summaries = []
            
            for i in range(0, len(chunk_summaries), group_size):
                group = chunk_summaries[i:i+group_size]
                group_num = i // group_size + 1
                total_groups = (len(chunk_summaries) + group_size - 1) // group_size
                
                print(f"   🔄 Processing group {group_num}/{total_groups} ({len(group)} parts)...")
                
                # Combine this group's summaries
                group_combined = "\n\n".join([
                    f"Part {j+1}:\n{summary}" 
                    for j, summary in enumerate(group, start=i)
                ])
                
                # Create intermediate summary for this group
                group_prompt = ChatPromptTemplate.from_template(
                    """You are combining multiple summaries from a technical meeting into one cohesive summary.

IMPORTANT: Write the summary entirely in ENGLISH, regardless of the language in the individual parts.

Individual summaries from parts of the meeting:
{text}

Create a COMPREHENSIVE summary IN ENGLISH that:
1. Combines all technical information
2. Organizes topics logically
3. Maintains all technical details and decisions
4. Includes action items and responsibilities
5. Removes redundancy while keeping unique information

COMBINED SUMMARY (IN ENGLISH):"""
                )
                
                group_chain = group_prompt | self.llm
                
                try:
                    group_response = group_chain.invoke({"text": group_combined})
                    intermediate_summary = group_response.content.strip()
                    
                    if len(intermediate_summary) == 0:
                        print(f"   ⚠️  Group {group_num}: Empty response, retrying...")
                        # Retry once
                        group_response = group_chain.invoke({"text": group_combined})
                        intermediate_summary = group_response.content.strip()
                        
                        if len(intermediate_summary) == 0:
                            print(f"   ❌ Group {group_num}: Still empty after retry, using concatenation fallback")
                            # Fallback: just concatenate the summaries with markers
                            intermediate_summary = "\n\n".join([
                                f"[Part {j+1}]\n{summary}" 
                                for j, summary in enumerate(group, start=i)
                            ])
                    
                    intermediate_summaries.append(intermediate_summary)
                    print(f"   ✓ Group {group_num}: {len(intermediate_summary)} chars")
                    
                except Exception as group_error:
                    print(f"   ❌ Group {group_num}: Error - {group_error}")
                    # Fallback: concatenate the group's summaries
                    fallback_summary = "\n\n".join([
                        f"[Part {j+1}]\n{summary}" 
                        for j, summary in enumerate(group, start=i)
                    ])
                    intermediate_summaries.append(fallback_summary)
                    print(f"   ⚠️  Group {group_num}: Using concatenation fallback ({len(fallback_summary)} chars)")
            
            print(f"   🔗 Combining {len(intermediate_summaries)} intermediate summaries into final summary...")
            
            # Now combine the intermediate summaries into final summary
            combined_text = "\n\n".join([
                f"Section {i+1}:\n{summary}" 
                for i, summary in enumerate(intermediate_summaries)
            ])
        else:
            # For smaller sets, directly combine all chunk summaries
            combined_text = "\n\n".join([f"Part {i+1}:\n{summary}" for i, summary in enumerate(chunk_summaries)])
        
        print(f"   📏 Combined text length: {len(combined_text)} chars")
        print(f"   🤖 Asking LLM to create final combined summary...")
        
        combine_prompt_template = ChatPromptTemplate.from_template(
            """You are combining multiple summaries of a technical software development meeting into one comprehensive summary.

IMPORTANT: Write the final summary entirely in ENGLISH, regardless of the language in the individual summaries.

Individual summaries from different parts of the meeting:
{combined_text}

Create a COMPREHENSIVE and DETAILED final summary IN ENGLISH that:
1. Combines all the technical information from the individual summaries
2. Organizes topics logically (architecture, decisions, tasks, team, etc.)
3. Maintains all technical details, system names, and specific decisions
4. Includes all action items and next steps mentioned
5. Preserves team member names and their responsibilities
6. Keeps the technical depth - don't oversimplify
7. Removes redundancy while keeping all unique information

FINAL COMPREHENSIVE SUMMARY (IN ENGLISH):"""
        )
        
        # Use a separate LLM instance with higher max_tokens for final combination
        # This ensures we have enough output tokens even with large input
        final_llm = ChatOpenAI(
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key,
            max_tokens=8192,  # Larger output budget for final summary
            temperature=self.settings.openai_temperature if self.settings.openai_temperature != 1.0 else 1.0,
        )
        
        combine_chain = combine_prompt_template | final_llm
        
        print("   🤖 Creating final summary...")
        final_response = combine_chain.invoke({"combined_text": combined_text})
        
        summary = final_response.content.strip()
        
        # Debug output
        print(f"   📊 Final summary length: {len(summary)} characters")
        if len(summary) == 0:
            print(f"   ⚠️  WARNING: Summary is empty!")
            print(f"   🔍 Response type: {type(final_response)}")
            print(f"   🔍 Has content attr: {hasattr(final_response, 'content')}")
            if hasattr(final_response, 'content'):
                print(f"   🔍 Content value: '{final_response.content}'")
        
        print("✅ Summary generated")
        return summary

    def generate_call_to_action(self, transcript: str, summary: str) -> List[str]:
        """
        Extract and generate actionable call-to-actions from the transcript.

        Args:
            transcript: The full transcript text
            summary: The generated summary

        Returns:
            A list of call-to-action items
        """
        print("🎯 Generating call-to-action items...")
        
        # For action items, we primarily use the summary
        # Only add transcript sample if summary is very short
        context = summary
        if len(summary) < 500 and len(transcript) > 0:
            sample_length = 15000
            transcript_sample = transcript[:sample_length]
            context = f"{summary}\n\nAdditional Context:\n{transcript_sample}"
        
        prompt_template = ChatPromptTemplate.from_template(
            """You are an expert at extracting actionable items from technical software development meetings.

Based on the following meeting summary, identify and list ALL specific actionable items, tasks, decisions, and next steps.

For each action item, be specific about:
- WHAT needs to be done
- WHO should do it (if mentioned)
- WHY it's needed (if clear from context)
- Technical details (systems, code, architecture affected)

Include:
- Tasks explicitly assigned or discussed
- Technical investigations or research needed
- Code changes or implementations planned
- Documentation to be created or updated  
- Meetings or discussions to be scheduled
- Decisions that need to be made
- Issues or blockers that need resolution

Meeting Summary:
{context}

List each action item on a separate line. Be comprehensive and include ALL actionable items mentioned.
Format: Just the action items, one per line, no numbering or bullets:"""
        )
        
        action_chain = prompt_template | self.llm
        
        print("   🔍 Extracting action items...")
        response = action_chain.invoke({"context": context})

        actions_text = response.content.strip()
        
        # Parse the actions into a list
        actions = []
        for line in actions_text.split("\n"):
            line = line.strip()
            # Remove common prefixes
            for prefix in ["•", "-", "*", "→", "►"]:
                if line.startswith(prefix):
                    line = line[1:].strip()
            # Remove numbering (1. 2. etc)
            if len(line) > 2 and line[0].isdigit() and line[1] in [".", ")", ":"]:
                line = line[2:].strip()
            # Keep substantial lines
            if len(line) > 10 and not line.startswith("#"):
                actions.append(line)
        
        print(f"✅ Generated {len(actions)} call-to-action items")
        return actions
