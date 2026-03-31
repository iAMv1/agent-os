---
name: communication-design
description: Use when you need to communicate anything clearly — explanations, documentation, presentations, or instructions. Transforms complex ideas into clear communication.
when_to_use: Writing documentation, explaining concepts, creating guides, preparing presentations, or when you need your message to be understood by a specific audience.
allowed-tools:
  - Read
  - Write
  - Edit
arguments:
  - audience
  - purpose
argument-hint: "[audience-description] [inform|persuade|instruct|document]"
---

# Communication Design

Transform complex ideas into clear, audience-appropriate communication. The best communication is the shortest path from your brain to someone else's understanding.

<HARD-GATE>
Do NOT write anything without first identifying the audience and their current knowledge level. Do NOT use jargon the audience doesn't know without defining it.
</HARD-GATE>

## The Iron Law

Every piece of communication must pass the "grandmother test" — could someone with no background in the topic understand the core message?

## When to Use

- Writing documentation or guides
- Explaining complex concepts
- Creating presentations
- Writing technical specifications
- Preparing status reports
- Any communication where misunderstanding has a cost

## When NOT to Use

- Quick notes to yourself
- Communication where the audience already has full context
- When the message is trivially simple

## The Process

### Phase 1: Audience Analysis

1. **Who is the audience?**
   - What do they already know?
   - What do they need to know?
   - What's their technical level?
   - What's their motivation for reading?

2. **Define the goal**
   - After reading, what should they know?
   - After reading, what should they be able to do?
   - After reading, what should they feel?

### Phase 2: Structure

3. **Choose the structure**
   | Structure | Best For | Pattern |
   |-----------|----------|---------|
   | **Pyramid** | General audience | Key message → supporting points → details |
   | **Chronological** | Processes, histories | First → then → finally |
   | **Problem-Solution** | Persuasion | Problem → impact → solution → benefits |
   | **How-To** | Instructions | Prerequisites → steps → verification |
   | **Reference** | Lookup | Organized catalog with cross-references |

4. **Outline before writing**
   - What goes in each section?
   - What's the flow between sections?
   - What can be cut?

### Phase 3: Write

5. **Write for scanning**
   - Short paragraphs (3-5 sentences max)
   - Clear headings and subheadings
   - Bullet points for lists
   - Bold for key terms
   - Code blocks for technical content

6. **Use the right language**
   - Active voice over passive
   - Concrete over abstract
   - Specific over vague
   - Short words over long words
   - Examples over descriptions

7. **Show, don't tell**
   <Good>
   - "The function returns null when the input is empty"
   - "Response time: 50ms (target: 100ms)"
   - "Example: `getUser(123)` returns `{id: 123, name: "Alice"}`"
   </Good>
   <Bad>
   - "The function handles edge cases appropriately"
   - "The system is fast"
   - "The API returns user data"
   </Bad>

### Phase 4: Refine

8. **Cut ruthlessly**
   - Remove every word that doesn't add meaning
   - Merge redundant sections
   - Move details to appendices
   - Kill your darlings

9. **Test comprehension**
   - Could someone act on this information?
   - Would someone new to the topic understand?
   - Would an expert find gaps or errors?

## Communication Quality Checklist

- [ ] Audience is identified and addressed at their level
- [ ] Goal is clear (inform/persuade/instruct)
- [ ] Structure matches the content type
- [ ] Every section has a clear purpose
- [ ] Language is appropriate for the audience
- [ ] Examples are concrete and relevant
- [ ] Nothing important is missing
- [ ] Nothing unnecessary is included
- [ ] Formatting aids scanning

## Integration

Related skills: `knowledge-synthesis`, `deep-research`, `strategic-planning`
