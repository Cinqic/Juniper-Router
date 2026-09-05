# ADR-0004: SFT before optional DPO

Status: accepted.

The project first establishes a reviewed supervised routing dataset and SFT
baseline. DPO is allowed only when a frozen evaluation shows a specific
preference-sensitive weakness, the chosen/rejected pairs are reviewed and
non-trivial, and the DPO candidate improves primary metrics without violating
hard gates or retention limits.
