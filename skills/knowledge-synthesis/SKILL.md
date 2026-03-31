---
name: knowledge-synthesis
description: Use when you need to combine information from multiple sources into coherent understanding. Transforms scattered facts into structured knowledge.
when_to_use: After research, when connecting dots between disparate information, building mental models, creating documentation, or when you have facts but need understanding.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
arguments:
  - topic
  - format
argument-hint: "[topic] [mental-model|framework|guide|reference|primer]"
---

# Knowledge Synthesis

Transform scattered information into structured, actionable knowledge. Goes beyond summarizing to create genuine understanding.

<HARD-GATE>
Do NOT produce a summary when a framework is needed. Do NOT list facts without showing relationships. Do NOT synthesize without identifying what's missing.
</HARD-GATE>

## The Iron Law

Every synthesis must answer: "So what?" — what does this knowledge enable that wasn't possible before?

## When to Use

- You've gathered information and need to make sense of it
- Multiple sources provide pieces of a larger picture
- You need to create documentation or guides
- You're building understanding before making decisions
- You need to transfer knowledge to others

## When NOT to Use

- Single-source information that just needs summarizing
- Raw data that needs analysis, not synthesis
- When you need more information before synthesizing

## The Process

### Phase 1: Gather & Map

1. **Collect all sources**
   - What information do we have?
   - What are the source types? (code, docs, articles, data)
   - How reliable is each source?

2. **Map the information space**
   ```
   Information Map:
   ├── Topic Area 1
   │   ├── Fact A (source, reliability)
   │   ├── Fact B (source, reliability)
   │   └── Connection: A → B because...
   ├── Topic Area 2
   │   └── ...
   └── Cross-cutting themes
       └── ...
   ```

### Phase 2: Find Patterns

3. **Identify relationships**
   - Causal: A causes B
   - Correlational: A and B change together
   - Hierarchical: A contains B
   - Sequential: A then B then C
   - Contradictory: A says X, B says not-X

4. **Find the underlying structure**
   - What principles explain the patterns?
   - What's the simplest model that fits the facts?
   - What would an expert in this domain recognize?

### Phase 3: Build the Synthesis

5. **Choose the right format**
   | Format | Best For | Structure |
   |--------|----------|-----------|
   | **Mental model** | Understanding concepts | Core principle → implications → examples |
   | **Framework** | Making decisions | Criteria → options → evaluation → recommendation |
   | **Guide** | Taking action | Prerequisites → steps → verification → troubleshooting |
   | **Reference** | Looking up facts | Organized catalog with cross-references |
   | **Primer** | Learning basics | Concepts → relationships → examples → next steps |

6. **Write the synthesis**
   ```
   Structure:
   ├── What This Is (1-2 sentences)
   ├── Why It Matters (the "so what?")
   ├── Core Principles (3-5 key ideas)
   ├── How It Works (mechanisms, relationships)
   ├── Examples (concrete illustrations)
   ├── Edge Cases (where it breaks down)
   ├── What's Missing (gaps in knowledge)
   └── Next Steps (how to use this knowledge)
   ```

### Phase 4: Validate

7. **Check against sources**
   - Does every claim trace back to a source?
   - Are contradictions resolved or acknowledged?
   - Is anything overstated?

8. **Test the synthesis**
   - Could someone use this to make a decision?
   - Could someone teach from this?
   - Would an expert find gaps or errors?

## Synthesis Quality Checklist

- [ ] Every claim has a source
- [ ] Relationships between facts are explicit
- [ ] The "so what?" is answered
- [ ] Contradictions are acknowledged
- [ ] Gaps in knowledge are identified
- [ ] Format matches the use case
- [ ] A novice could understand it
- [ ] An expert would find it accurate

## Anti-Slop Rules

<Good>
- "The pattern across all three sources is X, which suggests Y because..."
- "Source A contradicts Source B on point C. This may be because..."
- "What's missing from all sources is D, which matters because..."
</Good>

<Bad>
- "In summary, the sources say..."
- "There are many aspects to consider..."
- "It's a complex topic with many factors..."
</Bad>

## Integration

Related skills: `deep-research`, `decision-framework`, `learning-accelerator`, `communication-design`
