---
name: learning-accelerator
description: Use when you need to learn any new topic, technology, or skill as fast as possible. Creates optimized learning paths based on what you already know and what you need to know.
when_to_use: Learning a new technology, understanding a new codebase, picking up a new skill, or when you need to get up to speed on any topic quickly.
allowed-tools:
  - Read
  - Write
  - Edit
  - WebFetch
  - WebSearch
  - Bash
arguments:
  - topic
  - current-level
  - target-level
argument-hint: "[topic] [beginner|intermediate|advanced] [beginner|intermediate|advanced|expert]"
---

# Learning Accelerator

Learn anything as fast as possible by building on what you already know and focusing only on what's new.

<HARD-GATE>
Do NOT create a learning path without first identifying what the learner already knows. Do NOT include content the learner already understands.
</HARD-GATE>

## The Iron Law

Every minute of learning time must produce new knowledge — never review what's already known.

## When to Use

- Learning a new technology or framework
- Understanding a new codebase
- Picking up a new programming language
- Getting up to speed on any domain
- When you need to learn something quickly and thoroughly

## When NOT to Use

- When you already know the topic well
- When you have unlimited time and want a leisurely exploration
- When the topic is too small to warrant a structured approach

## The Process

### Phase 1: Knowledge Audit

1. **Map existing knowledge**
   - What do you already know that's related?
   - What concepts transfer from other domains?
   - What mental models already apply?

2. **Identify knowledge gaps**
   - What's completely new?
   - What's familiar but different here?
   - What's the same but with different names?

3. **Define the target**
   - What does "knowing this" look like?
   - What specific skills do you need?
   - What's the minimum viable knowledge?

### Phase 2: Learning Path Design

4. **Build the dependency graph**
   ```
   Concept A (prerequisite for B, C)
   ├── Concept B (prerequisite for D)
   │   └── Concept D (advanced)
   └── Concept C (prerequisite for E)
       └── Concept E (advanced)
   ```

5. **Create the learning sequence**
   - Start with prerequisites
   - Build up layer by layer
   - Practice after each concept
   - Connect to existing knowledge

6. **Estimate time**
   - How long per concept?
   - What's the total time?
   - What's the minimum viable path?

### Phase 3: Execute Learning

7. **Learn each concept**
   - Read the documentation/source
   - Build a mental model
   - Connect to existing knowledge
   - Test understanding with examples

8. **Practice immediately**
   - Apply each concept right away
   - Build something small with it
   - Identify gaps in understanding

9. **Teach it back**
   - Explain the concept in your own words
   - If you can't explain it, you don't understand it
   - Go back and fill gaps

### Phase 4: Consolidate

10. **Build the knowledge map**
    - What do you know now?
    - How do concepts connect?
    - What's still unclear?

11. **Identify next steps**
    - What should you learn next?
    - What projects would solidify this knowledge?
    - What resources are best for deepening?

## Learning Strategies by Type

| Type | Strategy | Focus |
|------|----------|-------|
| **Technology** | Build → Break → Fix | Hands-on projects |
| **Language** | Read → Write → Refactor | Code patterns |
| **Framework** | Tutorial → Clone → Customize | Architecture patterns |
| **Concept** | Explain → Example → Edge case | Mental models |
| **Tool** | Use → Explore → Master | Practical application |

## Learning Quality Checklist

- [ ] Existing knowledge is mapped
- [ ] Learning path is sequenced by dependencies
- [ ] Each concept has a practice exercise
- [ ] Understanding is tested by teaching back
- [ ] Knowledge map is complete
- [ ] Next steps are identified

## Integration

Related skills: `knowledge-synthesis`, `deep-research`, `problem-decomposition`
