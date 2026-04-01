---
name: market-research
description: Use when you need comprehensive market research, competitive analysis, industry trends, or strategic intelligence. Conducts deep multi-source research with structured synthesis and actionable insights. Self-wakes when market context is needed for any decision.
when_to_use: Market entry decisions, competitive analysis, industry research, product positioning, pricing strategy, customer analysis, trend forecasting, or any decision requiring market intelligence.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
  - WebSearch
  - TodoWrite
arguments:
  - topic
  - depth
  - focus
argument-hint: "[market-or-topic] [quick|standard|deep|comprehensive] [competitive|trends|customers|pricing|entry|comprehensive]"
---

# Market Research

Comprehensive market intelligence through multi-source investigation, competitive analysis, and structured synthesis. Produces actionable insights, not just data.

<HARD-GATE>
Do NOT present market data without citing sources. Do NOT present speculation as fact. Do NOT skip competitive analysis. Do NOT present findings without actionable recommendations.
</HARD-GATE>

## The Iron Law

Every market finding must have at least TWO independent sources confirming it, with explicit confidence levels and actionable implications.

## Self-Wake Triggers

This skill activates AUTOMATICALLY when:
- Making decisions about product direction or market positioning
- Evaluating competitors or market opportunities
- Planning go-to-market strategy
- Assessing market size or growth potential
- Any task where market context would change the approach

## Research Depth Levels

| Level | Sources | Time | Output | Use When |
|-------|---------|------|--------|----------|
| **quick** | 5-10 sources | 10-15 min | Key findings summary | Quick direction check |
| **standard** | 10-25 sources | 20-40 min | Structured report | Normal research needs |
| **deep** | 25-50 sources | 40-90 min | Comprehensive analysis | Strategic decisions |
| **comprehensive** | 50+ sources | 90-180 min | Full intelligence report | Critical market decisions |

## Research Focus Areas

| Focus | What It Covers | Key Questions |
|-------|---------------|---------------|
| **competitive** | Direct/indirect competitors, positioning, strengths/weaknesses | Who competes? How do they win? Where are gaps? |
| **trends** | Market trends, technology shifts, regulatory changes | Where is the market heading? What's emerging? |
| **customers** | Target segments, pain points, buying behavior | Who buys? Why do they buy? What do they value? |
| **pricing** | Pricing models, willingness to pay, price sensitivity | What's the pricing landscape? What works? |
| **entry** | Market entry barriers, requirements, strategies | How to enter? What's needed? What are risks? |
| **comprehensive** | All of the above | Complete market intelligence |

## The Process

### Phase 1: Scope Definition

1. **Define research objectives**
   - What decision will this research inform?
   - What would a complete answer look like?
   - What are the critical unknowns?

2. **Map the research landscape**
   ```
   Research Map:
   ├── Market Definition
   │   ├── Size and growth
   │   ├── Segments and sub-markets
   │   └── Geographic scope
   ├── Competitive Landscape
   │   ├── Direct competitors
   │   ├── Indirect competitors
   │   └── Substitute solutions
   ├── Customer Analysis
   │   ├── Target segments
   │   ├── Pain points and needs
   │   └── Buying behavior
   ├── Trends and Drivers
   │   ├── Technology trends
   │   ├── Regulatory changes
   │   └── Economic factors
   └── Opportunities and Threats
       ├── Market gaps
       ├── Emerging opportunities
       └── Potential threats
   ```

### Phase 2: Multi-Source Investigation

3. **Search systematically**
   - Start broad (market overview), then narrow (specific segments)
   - Use multiple search strategies and sources
   - Track what you've searched and found

4. **Source hierarchy** (most to least reliable)
   ```
   Tier 1: Primary Data
   ├── Company filings and earnings reports
   ├── Government statistics and reports
   ├── Academic research and studies
   └── Direct customer interviews/surveys

   Tier 2: Secondary Data
   ├── Industry reports (Gartner, Forrester, etc.)
   ├── Market research firms (Statista, IBISWorld, etc.)
   ├── Trade publications and journals
   └── Analyst reports and briefings

   Tier 3: Tertiary Data
   ├── News articles and press releases
   ├── Blog posts and opinion pieces
   ├── Social media and forums
   └── Wikipedia and general references
   ```

5. **Verify independently**
   - Cross-check findings across multiple sources
   - Note when sources disagree
   - Flag low-confidence findings
   - Document source reliability

### Phase 3: Competitive Analysis

6. **Map competitors**
   ```
   Competitive Matrix:
   | Competitor | Market Share | Strengths | Weaknesses | Pricing | Differentiator |
   |------------|-------------|-----------|------------|---------|----------------|
   | Competitor A | X% | List | List | $X | What makes them unique |
   | Competitor B | X% | List | List | $X | What makes them unique |
   ```

7. **Analyze positioning**
   - Positioning map (2-axis visualization)
   - Value proposition comparison
   - Feature parity analysis
   - Customer perception analysis

8. **Identify gaps**
   - Unmet customer needs
   - Underserved segments
   - Feature gaps in existing solutions
   - Pricing gaps

### Phase 4: Synthesis & Insights

9. **Organize findings**
   - Group by theme/category
   - Separate facts from interpretations
   - Identify patterns and contradictions

10. **Evaluate evidence**
    - **Strong evidence**: Multiple independent Tier 1-2 sources agree
    - **Medium evidence**: Single authoritative source or multiple Tier 3 sources
    - **Weak evidence**: Speculation, single non-authoritative source

11. **Generate insights**
    - What does this data mean?
    - What are the implications?
    - What actions should be taken?

### Phase 5: Report Generation

12. **Structure the report**
    ```
    Market Research Report: [Topic]
    ├── Executive Summary
    │   ├── Key findings (3-5 bullet points)
    │   ├── Market size and growth
    │   ├── Competitive landscape summary
    │   └── Key recommendations
    │
    ├── Market Overview
    │   ├── Market size and growth rate
    │   ├── Market segments
    │   ├── Geographic breakdown
    │   └── Market lifecycle stage
    │
    ├── Competitive Analysis
    │   ├── Competitor profiles (top 5-10)
    │   ├── Competitive matrix
    │   ├── Positioning analysis
    │   └── SWOT analysis
    │
    ├── Customer Analysis
    │   ├── Target segments
    │   ├── Customer pain points
    │   ├── Buying behavior
    │   └── Customer journey
    │
    ├── Trends and Drivers
    │   ├── Technology trends
    │   ├── Regulatory changes
    │   ├── Economic factors
    │   └── Social/cultural shifts
    │
    ├── Opportunities and Threats
    │   ├── Market gaps
    │   ├── Emerging opportunities
    │   ├── Potential threats
    │   └── Risk assessment
    │
    ├── Recommendations
    │   ├── Strategic recommendations
    │   ├── Tactical actions
    │   ├── Prioritized roadmap
    │   └── Risk mitigation
    │
    └── Appendix
        ├── Methodology
        ├── Source bibliography
        ├── Data tables
        └── Confidence levels by finding
    ```

13. **Write with precision**
    - State confidence levels explicitly for every finding
    - Cite sources for every claim
    - Distinguish facts from interpretations
    - Note limitations and caveats
    - Include actionable recommendations

## Confidence Calibration

| Confidence | Criteria | Language |
|------------|----------|----------|
| **High** | 3+ independent Tier 1-2 sources agree | "Confirmed:", "Verified:" |
| **Medium** | 2 sources agree, or single authoritative source | "Evidence suggests:", "Likely:" |
| **Low** | Single Tier 3 source, or speculation | "Possibly:", "May be:", "Uncertain:" |

## Anti-Slop Rules

<Good>
- "Market size: $X billion (2024), growing at Y% CAGR (Source: Gartner 2024, Statista 2024)"
- "Competitor A leads with X% market share, but is vulnerable in Y segment (Source: Forrester, company filings)"
- "Confidence: High (3 independent sources agree on trend direction)"
- "Recommendation: Enter X segment because [evidence-based reasoning]"
</Good>

<Bad>
- "The market is growing"
- "Competitors are doing well"
- "There's a lot of opportunity"
- Any finding without a cited source
- Recommendations without evidence
</Bad>

## Research Quality Checklist

- [ ] Research objectives are clearly defined
- [ ] Sources are from multiple tiers (not just one type)
- [ ] Every finding has at least 2 independent sources
- [ ] Confidence levels are stated for every finding
- [ ] Competitive analysis includes direct and indirect competitors
- [ ] Customer analysis covers segments, pain points, behavior
- [ ] Trends are identified with evidence
- [ ] Opportunities and threats are identified
- [ ] Recommendations are evidence-based and actionable
- [ ] Source bibliography is complete
- [ ] Limitations and caveats are documented

## Integration

Related skills: `deep-research`, `decision-framework`, `strategic-planning`, `knowledge-synthesis`, `risk-assessment`
