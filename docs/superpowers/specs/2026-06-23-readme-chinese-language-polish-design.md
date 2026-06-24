# Memory Pod README Chinese Language Polish Design

## Goal

Rewrite the Chinese half of `README.md` in concise, professional, natural
Simplified Chinese for open-source readers and technical hackathon judges,
without changing the English version, document structure, commands, links, or
technical meaning.

## Editorial Approach

Use a full native-language rewrite rather than isolated proofreading. Each
paragraph will be reconsidered as Chinese prose while remaining semantically
equivalent to its English counterpart.

The result should read as if it were originally written in Chinese:

- Prefer short, direct sentences and active constructions.
- Use natural transitions instead of reproducing English sentence order.
- Remove unnecessary subjects such as repeated “系统会” and “该路径”.
- Avoid promotional language and exaggerated claims.
- Preserve the measured tone appropriate for an open-source technical project.

## Terminology

Keep established product and ecosystem terms unchanged where consistency with
the interface matters:

- `Base Pod`
- `Shared Pod`
- `Pod Dock`
- `.mpod`
- CLI
- Ollama
- JSONL
- API

Use natural Chinese around those terms. Replace awkward literal translations
where they are not stable product labels:

| Current style | Preferred direction |
| --- | --- |
| 显式写回 | 主动保存为记忆 / 主动写入 |
| 输入框原位注入 | 直接回填当前输入框 |
| 本地表示 | 向量表示 |
| 容错润色 | 带降级机制的本地润色 |
| 活动 Pod 选择 | 当前选中的 Pod |
| 增强内容并粘贴回原位置 | 补充相关上下文后回填输入框 |

“增强提示词” may remain because it is already defined clearly and is used
consistently throughout the Chinese section.

## Scope

### In Scope

- Every prose paragraph, table description, heading that sounds translated,
  troubleshooting item, and limitation in the Chinese section.
- Consistent punctuation, spacing between Chinese and Latin text, and sentence
  rhythm.
- Clearer explanations of the product problem, workflow, privacy boundary, and
  macOS interaction.

### Out of Scope

- English content.
- Section order or information architecture.
- Shell commands, paths, environment variables, API names, and Markdown links.
- Product behavior, source code, or configuration.
- New claims, features, or omissions relative to the English section.

## Content Fidelity

The polished Chinese version must preserve these boundaries exactly:

- Memory Pod was built for the 2026 AI Hackathon at UC Berkeley.
- It is a working MVP, not a production-hardened service.
- The recommended experience is review-first.
- Memory Pod never auto-submits prompts.
- Imported Shared Pods are read-only.
- `.mpod` files omit embeddings and absolute local source paths.
- Author metadata is not cryptographically verified.
- Approved context leaves the local machine when the user sends it to an
  external AI provider.
- macOS hotkey flows require Accessibility permission and remain less portable
  than the CLI and copy flow.

## Validation

- Extend documentation tests with a small set of banned translation-like phrases
  and required natural replacements.
- Keep all existing bilingual structure, navigation, and local-link tests green.
- Compare Chinese commands, paths, environment variables, and links with the
  pre-edit section to confirm they remain unchanged.
- Run the complete repository test suite.

## Acceptance Criteria

- The Chinese section reads naturally to a Simplified Chinese technical reader.
- The opening is immediately understandable without sounding like a literal
  translation.
- Technical sections are concise, precise, and restrained.
- Stable product terms remain aligned with the UI and English README.
- No commands, links, safety statements, or product limitations are lost or
  altered.
