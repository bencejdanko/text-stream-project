---
authors: ["Bence Danko"]
date: "2025-2-24"
eyebrow: Research
hero: /mail.jpg
keywords: ["Kafka", "Hadoop", "Spark"]
dropcap: true
---

## ABSTRACT

===

Large Language Model (LLM) based Multi-Agents have achieved great success in performing tasks automatically. Practical implementations are centralized or layered: instead of digesting tasks in a single LLM stream, master agent(s) typically assign functional tasks to sub-agents that are scoped to particular actions, which are related back to the master agent for a coherent user response and side effects. However, there is a lack of literature and implementation of distributed and shared-message-pool multi-agent systems. These are systems which lack a hierarchical structure– agents share the same context pool, and can pipe their streamed outputs to each other indiscriminately. 

There is a lack of research in this area on how to effectively stream and monitor n-agent responses to a source-of-truth document, or pool, that can be re-contextualized by the multi-agent system for parallelized chain-of-thought (CoT) or task execution. This would be accomplished with a Kafka messaging system. In addition, there is a lack of literature describing how to effectively monitor, log, and snapshot distributed and shared-pooled streams and executions. We propose that these would be useful as a time-travel and version-control system, where agent task systems can be rolled-back in the case of distributed task failure among LLM agents. This would be a Hadoop MapReduce algorithm implementation. 

In addition, an efficient logging system can be used to trace back particular agent streams to evaluate their reasoning processes in the case of failure, or to implement privacy techniques (K-Anonymity) in sensitive tasks. LLMs may also benefit from re-contextualization of pre-stored reasoning or other documents that pertain to the current distributed reasoning. This implementation would entail the use of Locality Sensitive Hashing to compare the entire distributed document, or a particular agent’s current reasoning output, to pre-cached reasonings and documents, to make contextualizing more efficient and extensible.