---
name: optimization-engine
description: Use when you need to make anything faster, smaller, cheaper, or more efficient. Systematically identifies bottlenecks and applies proven optimization techniques.
when_to_use: Performance issues, cost reduction, resource optimization, process improvement, or when something works but could work significantly better.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - target
  - metric
argument-hint: "[what-to-optimize] [speed|cost|size|memory|throughput|all]"
---

# Optimization Engine

Make anything faster, smaller, cheaper, or more efficient. Measure first, optimize second, verify always.

<HARD-GATE>
Do NOT optimize without measuring the current state first. Do NOT optimize without verifying the improvement. Do NOT optimize anything that isn't a proven bottleneck.
</HARD-GATE>

## The Iron Law

Premature optimization is the root of all evil. Measure before optimizing. Verify after optimizing.

## When to Use

- Something is too slow, too expensive, or too large
- You need to improve performance or reduce costs
- You're designing a system and want to avoid known pitfalls
- You've identified a bottleneck and need to fix it
- You want to improve efficiency of any process

## When NOT to Use

- When something works well enough and optimization cost exceeds benefit
- When you don't have a way to measure the current state
- When the bottleneck hasn't been identified yet

## The Process

### Phase 1: Measure

1. **Establish baseline**
   - What's the current performance?
   - How do you measure it?
   - What's the target?
   - What's acceptable?

2. **Profile to find bottlenecks**
   - Where does time/money/resources go?
   - What's the 80/20 split? (20% of causes → 80% of effect)
   - What's the single biggest bottleneck?

3. **Prioritize optimization targets**
   ```
   | Component | Current | Target | Gap | Effort | Priority |
   |-----------|---------|--------|-----|--------|----------|
   | A         | 100ms   | 50ms   | 50ms| Low    | HIGH     |
   | B         | 500ms   | 200ms  | 300ms| High  | MEDIUM   |
   ```

### Phase 2: Optimize

4. **Apply optimization techniques**
   ```
   Optimization Hierarchy (most impact first):
   1. Algorithm: Better algorithm (O(n²) → O(n log n))
   2. Architecture: Better system design
   3. Data: Better data structures, caching
   4. Code: Better implementation
   5. Compiler: Better compilation flags
   6. Hardware: Better hardware
   ```

5. **Common optimization patterns**
   | Pattern | When to Use | Expected Impact |
   |---------|-------------|-----------------|
   | **Cache** | Repeated expensive operations | 10-100x |
   | **Batch** | Many small operations | 2-10x |
   | **Parallelize** | Independent operations | N cores |
   | **Lazy load** | Expensive initialization | Variable |
   | **Precompute** | Expensive runtime calculation | 10-100x |
   | **Reduce** | Unnecessary work | Variable |
   | **Index** | Slow lookups | 10-1000x |
   | **Compress** | Large data transfer | 2-10x |

### Phase 3: Verify

6. **Measure the improvement**
   - Same measurement method as baseline
   - Same conditions as baseline
   - Document the before/after

7. **Check for regressions**
   - Did optimization break anything?
   - Did it introduce new bottlenecks?
   - Is the improvement consistent?

8. **Document the optimization**
   - What was optimized
   - How it was optimized
   - Before/after measurements
   - Tradeoffs made

## Optimization Quality Checklist

- [ ] Baseline is measured and documented
- [ ] Bottleneck is identified (not guessed)
- [ ] Optimization targets highest-impact area
- [ ] Technique is appropriate for the bottleneck
- [ ] Improvement is measured and verified
- [ ] No regressions introduced
- [ ] Tradeoffs are documented

## Integration

Related skills: `quality-assurance`, `problem-decomposition`, `deep-research`
