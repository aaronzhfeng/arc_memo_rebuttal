"""
Memory Analysis for ArcMemo
============================

Analyzes memory behavior to validate conceptual learning vs memorization:
1. Redundancy: Semantic similarity between concepts
2. Transferability: Cross-puzzle concept reuse
3. Self-retrieval: Same-puzzle retrieval rates
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
import warnings

# Optional imports with fallback
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_ML_LIBS = True
except ImportError:
    HAS_ML_LIBS = False
    warnings.warn("sentence-transformers or scikit-learn not installed. Install with: pip install sentence-transformers scikit-learn")


@dataclass
class RedundancyResult:
    """Results from redundancy analysis"""
    total_concepts: int
    redundant_pairs: int
    redundancy_rate: float
    concept_clusters: List[List[str]]
    similarity_matrix: Optional[List[List[float]]] = None
    top_similar_pairs: List[Tuple[str, str, float]] = None


@dataclass
class TransferabilityResult:
    """Results from transferability analysis"""
    total_retrievals: int
    cross_puzzle_retrievals: int
    same_puzzle_retrievals: int
    transfer_rate: float
    self_retrieval_rate: float
    per_puzzle_breakdown: Dict[str, Dict[str, Any]] = None
    most_transferred_concepts: List[Tuple[str, int]] = None


@dataclass
class MemoryAnalysisReport:
    """Complete memory analysis report"""
    redundancy: Optional[RedundancyResult]
    transferability: Optional[TransferabilityResult]
    interpretation: str
    metadata: Dict[str, Any]


class MemoryAnalyzer:
    """
    Analyzes ArcMemo memory behavior
    """
    
    def __init__(self, similarity_threshold: float = 0.85, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Args:
            similarity_threshold: Threshold for considering concepts redundant (default: 0.85)
            model_name: Sentence transformer model to use
        """
        self.similarity_threshold = similarity_threshold
        self.model_name = model_name
        self.model = None
        
        if HAS_ML_LIBS:
            print(f"Loading sentence transformer model: {model_name}")
            self.model = SentenceTransformer(model_name)
        else:
            print("Warning: ML libraries not available. Redundancy analysis will be skipped.")
    
    def load_concepts(self, concepts_path: str) -> Dict[str, Any]:
        """Load concepts from compressed memory file"""
        print(f"Loading concepts from: {concepts_path}")
        with open(concepts_path, 'r') as f:
            data = json.load(f)
        
        concepts = data.get('concepts', {})
        print(f"Loaded {len(concepts)} concepts")
        return concepts
    
    def load_retrievals(self, retrievals_path: str) -> Dict[str, List[str]]:
        """
        Load retrieval logs
        
        Expected format: {puzzle_id: [retrieved_concept_ids]}
        """
        print(f"Loading retrievals from: {retrievals_path}")
        with open(retrievals_path, 'r') as f:
            retrievals = json.load(f)
        
        total_retrievals = sum(len(v) for v in retrievals.values())
        print(f"Loaded {len(retrievals)} puzzles with {total_retrievals} total retrievals")
        return retrievals
    
    def analyze_redundancy(self, concepts: Dict[str, Any], skip_contradiction: bool = False) -> RedundancyResult:
        """
        Analyze concept redundancy via semantic similarity
        
        Args:
            concepts: Dictionary of concept definitions
            skip_contradiction: If True, skip expensive contradiction detection
        """
        if not HAS_ML_LIBS:
            print("Skipping redundancy analysis (ML libraries not available)")
            return RedundancyResult(
                total_concepts=len(concepts),
                redundant_pairs=0,
                redundancy_rate=0.0,
                concept_clusters=[]
            )
        
        print("\n=== Redundancy Analysis ===")
        concept_ids = list(concepts.keys())
        n_concepts = len(concept_ids)
        
        # Build concept descriptions for embedding
        descriptions = []
        for cid in concept_ids:
            concept = concepts[cid]
            desc_parts = [
                f"Name: {concept.get('name', 'unknown')}",
                f"Kind: {concept.get('kind', 'unknown')}"
            ]
            if concept.get('description'):
                desc_parts.append(f"Description: {concept['description']}")
            if concept.get('parameters'):
                params = ', '.join([p.get('name', '') for p in concept['parameters']])
                desc_parts.append(f"Parameters: {params}")
            
            descriptions.append(' | '.join(desc_parts))
        
        print(f"Computing embeddings for {n_concepts} concepts...")
        embeddings = self.model.encode(descriptions, show_progress_bar=True)
        
        print("Computing similarity matrix...")
        similarity_matrix = cosine_similarity(embeddings)
        
        # Find redundant pairs (above threshold, excluding self-similarity)
        redundant_pairs = []
        seen_pairs = set()
        
        for i in range(n_concepts):
            for j in range(i + 1, n_concepts):
                sim = similarity_matrix[i, j]
                if sim >= self.similarity_threshold:
                    pair = tuple(sorted([concept_ids[i], concept_ids[j]]))
                    if pair not in seen_pairs:
                        redundant_pairs.append((concept_ids[i], concept_ids[j], float(sim)))
                        seen_pairs.add(pair)
        
        redundancy_rate = len(redundant_pairs) / (n_concepts * (n_concepts - 1) / 2) if n_concepts > 1 else 0.0
        
        print(f"Found {len(redundant_pairs)} redundant pairs ({redundancy_rate*100:.2f}% redundancy)")
        
        # Cluster redundant concepts
        clusters = self._cluster_redundant_concepts(redundant_pairs, concept_ids)
        print(f"Formed {len(clusters)} concept clusters")
        
        # Get top similar pairs
        top_pairs = sorted(redundant_pairs, key=lambda x: x[2], reverse=True)[:10]
        
        return RedundancyResult(
            total_concepts=n_concepts,
            redundant_pairs=len(redundant_pairs),
            redundancy_rate=redundancy_rate,
            concept_clusters=clusters,
            similarity_matrix=similarity_matrix.tolist(),
            top_similar_pairs=[(p[0], p[1], p[2]) for p in top_pairs]
        )
    
    def _cluster_redundant_concepts(self, redundant_pairs: List[Tuple[str, str, float]], 
                                   concept_ids: List[str]) -> List[List[str]]:
        """Group redundant concepts into clusters using union-find"""
        # Build adjacency list
        graph = defaultdict(set)
        for c1, c2, _ in redundant_pairs:
            graph[c1].add(c2)
            graph[c2].add(c1)
        
        # Find connected components
        visited = set()
        clusters = []
        
        for concept in concept_ids:
            if concept not in visited and concept in graph:
                cluster = []
                stack = [concept]
                while stack:
                    node = stack.pop()
                    if node not in visited:
                        visited.add(node)
                        cluster.append(node)
                        stack.extend(graph[node] - visited)
                
                if len(cluster) > 1:
                    clusters.append(sorted(cluster))
        
        return sorted(clusters, key=len, reverse=True)
    
    def analyze_transferability(self, concepts: Dict[str, Any], 
                               retrievals: Dict[str, List[str]]) -> TransferabilityResult:
        """
        Analyze concept transferability across puzzles
        
        Args:
            concepts: Dictionary of concept definitions
            retrievals: {puzzle_id: [retrieved_concept_ids]}
        """
        print("\n=== Transferability Analysis ===")
        
        # Extract puzzle origin for each concept (from concept ID format: puzzle_id_concept_num)
        concept_origins = {}
        for cid in concepts.keys():
            # Parse concept ID to get origin puzzle
            parts = cid.rsplit('_', 1)
            if len(parts) == 2:
                origin_puzzle = parts[0]
                concept_origins[cid] = origin_puzzle
            else:
                concept_origins[cid] = 'unknown'
        
        # Analyze retrievals
        total_retrievals = 0
        cross_puzzle_retrievals = 0
        same_puzzle_retrievals = 0
        per_puzzle_stats = {}
        concept_transfer_counts = defaultdict(int)
        
        for puzzle_id, retrieved_ids in retrievals.items():
            puzzle_cross = 0
            puzzle_same = 0
            
            for concept_id in retrieved_ids:
                total_retrievals += 1
                origin = concept_origins.get(concept_id, 'unknown')
                
                if origin == puzzle_id:
                    same_puzzle_retrievals += 1
                    puzzle_same += 1
                elif origin != 'unknown':
                    cross_puzzle_retrievals += 1
                    puzzle_cross += 1
                    concept_transfer_counts[concept_id] += 1
            
            per_puzzle_stats[puzzle_id] = {
                'total_retrievals': len(retrieved_ids),
                'cross_puzzle': puzzle_cross,
                'same_puzzle': puzzle_same,
                'transfer_rate': puzzle_cross / len(retrieved_ids) if retrieved_ids else 0.0
            }
        
        transfer_rate = cross_puzzle_retrievals / total_retrievals if total_retrievals > 0 else 0.0
        self_retrieval_rate = same_puzzle_retrievals / total_retrievals if total_retrievals > 0 else 0.0
        
        print(f"Total retrievals: {total_retrievals}")
        print(f"Cross-puzzle retrievals: {cross_puzzle_retrievals} ({transfer_rate*100:.2f}%)")
        print(f"Same-puzzle retrievals: {same_puzzle_retrievals} ({self_retrieval_rate*100:.2f}%)")
        
        # Get most transferred concepts
        most_transferred = sorted(concept_transfer_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return TransferabilityResult(
            total_retrievals=total_retrievals,
            cross_puzzle_retrievals=cross_puzzle_retrievals,
            same_puzzle_retrievals=same_puzzle_retrievals,
            transfer_rate=transfer_rate,
            self_retrieval_rate=self_retrieval_rate,
            per_puzzle_breakdown=per_puzzle_stats,
            most_transferred_concepts=most_transferred
        )
    
    def generate_interpretation(self, redundancy: Optional[RedundancyResult],
                               transferability: Optional[TransferabilityResult]) -> str:
        """Generate human-readable interpretation for rebuttal"""
        lines = ["=" * 80]
        lines.append("MEMORY ANALYSIS INTERPRETATION")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        
        if transferability:
            transfer_status = "✓ STRONG" if transferability.transfer_rate > 0.7 else \
                            "⚠ MODERATE" if transferability.transfer_rate > 0.4 else \
                            "✗ WEAK"
            lines.append(f"Transfer Rate: {transferability.transfer_rate*100:.1f}% {transfer_status}")
            lines.append(f"Self-Retrieval: {transferability.self_retrieval_rate*100:.1f}% " + 
                        ("✓ LOW" if transferability.self_retrieval_rate < 0.3 else "⚠ HIGH"))
        
        if redundancy:
            lines.append(f"Redundancy: {redundancy.redundancy_rate*100:.1f}% " +
                        ("(Common patterns)" if redundancy.redundancy_rate > 0.1 else "(Unique concepts)"))
            lines.append(f"Concept Clusters: {len(redundancy.concept_clusters)}")
        
        lines.append("")
        
        # Detailed interpretation
        lines.append("INTERPRETATION FOR REBUTTAL")
        lines.append("-" * 80)
        lines.append("")
        
        if transferability:
            lines.append("**Transferability Analysis:**")
            lines.append("")
            lines.append(f"We analyzed {transferability.total_retrievals} concept retrievals across puzzles.")
            lines.append(f"Results show {transferability.transfer_rate*100:.1f}% cross-puzzle retrieval rate,")
            lines.append(f"with only {transferability.self_retrieval_rate*100:.1f}% self-retrieval.")
            lines.append("")
            
            if transferability.transfer_rate > 0.7:
                lines.append("This demonstrates STRONG evidence of genuine abstraction and conceptual reuse")
                lines.append("rather than simple solution memorization. The system learns generalizable")
                lines.append("patterns that transfer effectively across different problems.")
            elif transferability.transfer_rate > 0.4:
                lines.append("This shows MODERATE evidence of concept transfer. While the system does")
                lines.append("reuse concepts across puzzles, there is room for improvement in abstraction.")
            else:
                lines.append("This indicates LIMITED cross-puzzle transfer. The system may be learning")
                lines.append("puzzle-specific rather than generalizable concepts.")
            lines.append("")
        
        if redundancy:
            lines.append("**Redundancy Analysis:**")
            lines.append("")
            lines.append(f"Analyzed {redundancy.total_concepts} concepts, finding {redundancy.redundant_pairs}")
            lines.append(f"highly similar pairs ({redundancy.redundancy_rate*100:.1f}% redundancy rate).")
            lines.append("")
            
            if redundancy.redundancy_rate > 0.1:
                lines.append("This indicates the emergence of common reusable patterns discovered")
                lines.append("independently across different puzzles, validating genuine abstraction.")
            else:
                lines.append("Low redundancy suggests concepts are largely unique, which could indicate")
                lines.append("either highly diverse abstraction or puzzle-specific learning.")
            lines.append("")
            
            if redundancy.concept_clusters:
                lines.append(f"Top {min(3, len(redundancy.concept_clusters))} Concept Clusters:")
                for i, cluster in enumerate(redundancy.concept_clusters[:3], 1):
                    lines.append(f"  {i}. {len(cluster)} concepts: {', '.join(cluster[:3])}" +
                               (f" + {len(cluster)-3} more" if len(cluster) > 3 else ""))
                lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 80)
        
        if transferability and transferability.transfer_rate > 0.6:
            lines.append("✓ Memory shows strong generalization. Suitable for rebuttal claims.")
        elif transferability and transferability.transfer_rate > 0.4:
            lines.append("⚠ Consider highlighting specific successful transfer examples in rebuttal.")
        
        if transferability and transferability.self_retrieval_rate > 0.4:
            lines.append("⚠ High self-retrieval rate. May want to investigate why.")
        
        lines.append("")
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def run_full_analysis(self, concepts_path: str, 
                         retrievals_path: Optional[str] = None,
                         skip_contradiction: bool = False) -> MemoryAnalysisReport:
        """
        Run complete memory analysis
        
        Args:
            concepts_path: Path to concepts JSON file
            retrievals_path: Optional path to retrievals JSON file
            skip_contradiction: Skip contradiction detection (faster)
        """
        print("\n" + "=" * 80)
        print("ARCMEMO MEMORY ANALYSIS")
        print("=" * 80)
        
        # Load data
        concepts = self.load_concepts(concepts_path)
        retrievals = None
        if retrievals_path:
            retrievals = self.load_retrievals(retrievals_path)
        
        # Run analyses
        redundancy_result = self.analyze_redundancy(concepts, skip_contradiction=skip_contradiction)
        
        transferability_result = None
        if retrievals:
            transferability_result = self.analyze_transferability(concepts, retrievals)
        else:
            print("\nSkipping transferability analysis (no retrieval data provided)")
        
        # Generate interpretation
        interpretation = self.generate_interpretation(redundancy_result, transferability_result)
        
        # Create report
        report = MemoryAnalysisReport(
            redundancy=redundancy_result,
            transferability=transferability_result,
            interpretation=interpretation,
            metadata={
                'concepts_file': concepts_path,
                'retrievals_file': retrievals_path,
                'similarity_threshold': self.similarity_threshold,
                'model': self.model_name
            }
        )
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
        return report
    
    @staticmethod
    def save_report(report: MemoryAnalysisReport, output_path: str):
        """Save analysis report to JSON file"""
        print(f"\nSaving report to: {output_path}")
        
        # Convert to dict
        report_dict = {
            'metadata': report.metadata,
            'redundancy': asdict(report.redundancy) if report.redundancy else None,
            'transferability': asdict(report.transferability) if report.transferability else None,
            'interpretation': report.interpretation
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        # Save interpretation as separate text file
        interp_path = output_path.replace('.json', '_interpretation.txt')
        with open(interp_path, 'w') as f:
            f.write(report.interpretation)
        
        print(f"Saved interpretation to: {interp_path}")

