"""
Performance Tests for Adaptive Memory System
Gate 3: Performance Benchmarks

Tests system performance under load:
1. Single evaluation speed (<50ms target)
2. Batch processing throughput (>100/sec target)
3. Memory footprint (<100MB for 1000 memories)
4. Component performance (evaluator <10ms, classifier <5ms, parser <5ms)
5. Scalability under load

Migrated from: tests/test_adaptive_memory_performance.py
"""

import sys
import time

import pytest

from pattern_agentic_memory.core.command_parser import UserMemoryCommandParser
from pattern_agentic_memory.core.importance_evaluator import MemoryImportanceEvaluator
from pattern_agentic_memory.core.memory_system import AdaptiveMemoryOrchestrator
from pattern_agentic_memory.core.tier_classifier import H200TierClassifier


class TestSingleEvaluationPerformance:
    """Gate 3: Performance - Single Memory Evaluation Speed"""

    @pytest.mark.asyncio
    async def test_single_evaluation_speed_simple_content(self):
        """Single memory evaluation should complete in <50ms (simple content)"""
        orchestrator = AdaptiveMemoryOrchestrator()

        start = time.time()

        decision = await orchestrator.process_memory_candidate(
            content="Test memory for performance evaluation", context={}, existing_memories=None
        )

        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 50, f"Evaluation took {elapsed_ms:.2f}ms (target: <50ms)"
        assert decision is not None

    @pytest.mark.asyncio
    async def test_single_evaluation_speed_complex_content(self):
        """Single evaluation with complex content and context (<50ms)"""
        orchestrator = AdaptiveMemoryOrchestrator()

        complex_content = """
        Important framework methodology: Real-time validation prevents production bugs.
        Remember this critical pattern. Actually, correction: the unexpected result
        from failed validation shows we need a different approach.
        """

        complex_context = {
            "corrects_previous_error": True,
            "unexpected_result": True,
            "validation_result": "failed",
            "is_framework_principle": True,
        }

        start = time.time()

        decision = await orchestrator.process_memory_candidate(
            content=complex_content, context=complex_context, existing_memories=[]
        )

        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < 50, f"Complex evaluation took {elapsed_ms:.2f}ms (target: <50ms)"
        assert decision is not None

    @pytest.mark.asyncio
    async def test_single_evaluation_speed_with_existing_memories(self):
        """Single evaluation with 10 existing memories (<50ms)"""
        orchestrator = AdaptiveMemoryOrchestrator()

        existing = [f"Previous memory about topic {i} with various content" for i in range(10)]

        start = time.time()

        decision = await orchestrator.process_memory_candidate(
            content="New memory content to compare against existing",
            context={},
            existing_memories=existing,
        )

        elapsed_ms = (time.time() - start) * 1000

        assert (
            elapsed_ms < 50
        ), f"Evaluation with existing memories took {elapsed_ms:.2f}ms (target: <50ms)"
        assert decision is not None

    @pytest.mark.asyncio
    async def test_average_evaluation_speed_100_samples(self):
        """Average speed over 100 evaluations should be <50ms"""
        orchestrator = AdaptiveMemoryOrchestrator()

        test_memories = [
            f"Test memory content variation {i} with different keywords" for i in range(100)
        ]

        times = []

        for content in test_memories:
            start = time.time()

            await orchestrator.process_memory_candidate(
                content=content, context={}, existing_memories=None
            )

            elapsed_ms = (time.time() - start) * 1000
            times.append(elapsed_ms)

        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)

        print("\nPerformance stats (100 samples):")
        print(f"  Average: {avg_time:.2f}ms")
        print(f"  Min: {min_time:.2f}ms")
        print(f"  Max: {max_time:.2f}ms")

        assert avg_time < 50, f"Average evaluation time {avg_time:.2f}ms exceeds target (50ms)"


class TestBatchThroughputPerformance:
    """Gate 3: Performance - Batch Processing Throughput"""

    @pytest.mark.asyncio
    async def test_batch_throughput_100_memories(self):
        """Process 100 memories in <1 second (>100/sec throughput)"""
        orchestrator = AdaptiveMemoryOrchestrator()

        test_memories = [f"Test memory content number {i}" for i in range(100)]

        start = time.time()

        for content in test_memories:
            await orchestrator.process_memory_candidate(
                content=content, context={}, existing_memories=None
            )

        elapsed = time.time() - start
        throughput = len(test_memories) / elapsed

        print("\nBatch throughput (100 memories):")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Throughput: {throughput:.1f} memories/sec")

        assert throughput > 100, f"Throughput {throughput:.1f}/sec below target (>100/sec)"

    @pytest.mark.asyncio
    async def test_batch_throughput_200_memories(self):
        """Process 200 memories maintaining >100/sec throughput"""
        orchestrator = AdaptiveMemoryOrchestrator()

        test_memories = [
            f"Memory content variant {i} with keywords framework bug fix working"
            for i in range(200)
        ]

        start = time.time()

        for content in test_memories:
            await orchestrator.process_memory_candidate(
                content=content, context={}, existing_memories=None
            )

        elapsed = time.time() - start
        throughput = len(test_memories) / elapsed

        print("\nBatch throughput (200 memories):")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Throughput: {throughput:.1f} memories/sec")

        assert throughput > 100, f"Throughput {throughput:.1f}/sec below target (>100/sec)"

    @pytest.mark.asyncio
    async def test_batch_throughput_mixed_complexity(self):
        """Process batch with mixed complexity maintaining throughput"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Mix of simple and complex memories
        test_memories = []
        for i in range(150):
            if i % 3 == 0:
                # Complex memory with context
                content = (
                    f"Important framework principle {i}: Remember this critical validation pattern"
                )
                test_memories.append((content, {"corrects_previous_error": True}))
            elif i % 3 == 1:
                # Medium memory
                content = f"Bug fix solution {i} deployed successfully"
                test_memories.append((content, {}))
            else:
                # Simple memory
                content = f"Working on task {i}"
                test_memories.append((content, {"is_temporary": True}))

        start = time.time()

        for content, context in test_memories:
            await orchestrator.process_memory_candidate(
                content=content, context=context, existing_memories=None
            )

        elapsed = time.time() - start
        throughput = len(test_memories) / elapsed

        print("\nBatch throughput (150 mixed complexity):")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Throughput: {throughput:.1f} memories/sec")

        assert (
            throughput > 100
        ), f"Mixed batch throughput {throughput:.1f}/sec below target (>100/sec)"


class TestMemoryFootprint:
    """Gate 3: Performance - Memory Resource Usage"""

    @pytest.mark.asyncio
    async def test_working_memory_buffer_size_1000_items(self):
        """1000 items in working memory should use <100MB"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Get baseline memory
        import gc

        gc.collect()
        sys.getsizeof(orchestrator.memory_buffer) / (1024 * 1024)

        # Add 1000 memories
        for i in range(1000):
            content = f"Memory content {i} with some text to simulate realistic size"
            decision = await orchestrator.process_memory_candidate(
                content=content, context={}, existing_memories=None
            )
            orchestrator.add_to_working_memory(content, decision)

        # Measure memory usage
        buffer_size_mb = sys.getsizeof(orchestrator.memory_buffer) / (1024 * 1024)

        # Estimate total size including content
        total_estimate_mb = 0
        for item in orchestrator.memory_buffer:
            total_estimate_mb += sys.getsizeof(item) / (1024 * 1024)
            total_estimate_mb += sys.getsizeof(item.get("content", "")) / (1024 * 1024)
            total_estimate_mb += sys.getsizeof(item.get("decision", {})) / (1024 * 1024)

        print("\nMemory footprint (1000 items):")
        print(f"  Buffer structure: {buffer_size_mb:.2f}MB")
        print(f"  Total estimate: {total_estimate_mb:.2f}MB")

        assert (
            total_estimate_mb < 100
        ), f"Memory footprint {total_estimate_mb:.2f}MB exceeds target (100MB)"

    @pytest.mark.asyncio
    async def test_batch_queue_memory_efficiency(self):
        """Batch queue filtering should not duplicate memory"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Add various memories
        for i in range(500):
            if i % 2 == 0:
                content = f"Framework principle {i}"
                context = {"is_framework_principle": True}
            else:
                content = f"Working memory {i}"
                context = {"is_temporary": True}

            decision = await orchestrator.process_memory_candidate(
                content=content, context=context, existing_memories=[]
            )
            orchestrator.add_to_working_memory(content, decision)

        # Get batch queue (should not duplicate)
        batch_queue = orchestrator.get_batch_queue()

        buffer_size = sys.getsizeof(orchestrator.memory_buffer) / (1024 * 1024)
        queue_size = sys.getsizeof(batch_queue) / (1024 * 1024)

        print("\nMemory efficiency (500 items):")
        print(f"  Buffer: {buffer_size:.2f}MB")
        print(f"  Queue: {queue_size:.2f}MB")
        print(f"  Queue items: {len(batch_queue)}")

        # Queue should reference, not duplicate (allow 60% for container overhead on small datasets)
        assert queue_size < buffer_size * 0.6, "Batch queue appears to duplicate data"


class TestComponentPerformance:
    """Gate 3: Performance - Individual Component Speed"""

    def test_importance_evaluator_speed(self):
        """MemoryImportanceEvaluator should evaluate in <10ms"""
        evaluator = MemoryImportanceEvaluator()

        times = []
        for i in range(100):
            content = f"Test content {i} with important keywords correction unexpected"
            context = {"corrects_previous_error": True}
            existing = [f"Existing memory {j}" for j in range(10)]

            start = time.time()
            score, reasoning = evaluator.evaluate_memory_candidate(content, context, existing)
            elapsed_ms = (time.time() - start) * 1000

            times.append(elapsed_ms)

        avg_time = sum(times) / len(times)

        print("\nImportanceEvaluator performance (100 samples):")
        print(f"  Average: {avg_time:.2f}ms")

        assert avg_time < 10, f"Evaluator average {avg_time:.2f}ms exceeds target (10ms)"

    def test_tier_classifier_speed(self):
        """H200TierClassifier should classify in <5ms"""
        classifier = H200TierClassifier()

        times = []
        for i in range(100):
            content = f"Framework methodology for bug fix solution working on task {i}"
            context = {"is_framework_principle": i % 4 == 0}

            start = time.time()
            tier, decay = classifier.classify_memory_tier(content, context)
            elapsed_ms = (time.time() - start) * 1000

            times.append(elapsed_ms)

        avg_time = sum(times) / len(times)

        print("\nTierClassifier performance (100 samples):")
        print(f"  Average: {avg_time:.2f}ms")

        assert avg_time < 5, f"Classifier average {avg_time:.2f}ms exceeds target (5ms)"

    def test_command_parser_speed(self):
        """UserMemoryCommandParser should parse in <5ms"""
        parser = UserMemoryCommandParser()

        times = []
        test_messages = [
            "Remember this important pattern",
            "Save this configuration",
            "Lesson learned about validation",
            "Regular message without commands",
            "This is important information",
            "Working on the implementation",
            "Always validate before deploy",
            "You should check the logs",
        ]

        for _ in range(100):
            for message in test_messages:
                start = time.time()
                parser.parse_user_intent(message)
                elapsed_ms = (time.time() - start) * 1000
                times.append(elapsed_ms)

        avg_time = sum(times) / len(times)

        print(f"\nCommandParser performance ({len(times)} samples):")
        print(f"  Average: {avg_time:.2f}ms")

        assert avg_time < 5, f"Parser average {avg_time:.2f}ms exceeds target (5ms)"


class TestScalabilityPerformance:
    """Gate 3: Performance - Scalability Under Load"""

    @pytest.mark.asyncio
    async def test_performance_degradation_with_large_existing_memories(self):
        """Performance should not degrade significantly with many existing memories"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Test with increasing numbers of existing memories
        memory_counts = [0, 10, 50, 100]
        results = []

        for count in memory_counts:
            existing = [f"Existing memory {i} with content" for i in range(count)]

            start = time.time()
            for i in range(20):  # Process 20 memories
                await orchestrator.process_memory_candidate(
                    content=f"New memory {i}", context={}, existing_memories=existing
                )
            elapsed_ms = (time.time() - start) * 1000 / 20  # Average per memory

            results.append((count, elapsed_ms))

        print("\nScalability with existing memories:")
        for count, time_ms in results:
            print(f"  {count} existing: {time_ms:.2f}ms avg")

        # Performance should not degrade more than 2x
        baseline = results[0][1]
        max_time = results[-1][1]
        degradation = max_time / baseline if baseline > 0 else 1

        assert degradation < 2.0, f"Performance degraded {degradation:.1f}x (target: <2x)"

    @pytest.mark.asyncio
    async def test_concurrent_processing_simulation(self):
        """Simulate concurrent processing with rapid sequential calls"""
        orchestrator = AdaptiveMemoryOrchestrator()

        # Simulate 50 rapid-fire requests
        start = time.time()

        for i in range(50):
            decision = await orchestrator.process_memory_candidate(
                content=f"Rapid memory {i}", context={}, existing_memories=None
            )
            orchestrator.add_to_working_memory(f"Rapid memory {i}", decision)

        elapsed = time.time() - start
        throughput = 50 / elapsed

        print("\nConcurrent processing simulation (50 requests):")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Throughput: {throughput:.1f} requests/sec")

        assert throughput > 100, f"Concurrent throughput {throughput:.1f}/sec below target"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])  # -s to show print statements
