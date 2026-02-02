"""
Memory Management Utilities
Optimize memory usage for Raspberry Pi
"""

import gc
import sys
import psutil
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Memory management for resource-constrained environments
    
    Features:
    - Monitor memory usage
    - Force garbage collection
    - Batch processing to limit memory
    - Memory usage decorators
    """
    
    @staticmethod
    def get_memory_usage() -> dict:
        """
        Get current memory usage
        
        Returns:
            Dictionary with memory stats
        """
        process = psutil.Process()
        mem_info = process.memory_info()
        
        return {
            'rss_mb': mem_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': mem_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def get_system_memory() -> dict:
        """
        Get system memory stats
        
        Returns:
            Dictionary with system memory stats
        """
        mem = psutil.virtual_memory()
        
        return {
            'total_mb': mem.total / (1024 * 1024),
            'available_mb': mem.available / (1024 * 1024),
            'used_mb': mem.used / (1024 * 1024),
            'percent': mem.percent
        }
    
    @staticmethod
    def force_gc():
        """Force garbage collection"""
        collected = gc.collect()
        logger.debug(f"Garbage collected: {collected} objects")
        return collected
    
    @staticmethod
    def print_memory_stats():
        """Print memory statistics"""
        proc_mem = MemoryManager.get_memory_usage()
        sys_mem = MemoryManager.get_system_memory()
        
        print("\n" + "="*70)
        print("💾 MEMORY STATISTICS")
        print("="*70)
        
        print(f"\n📊 Process Memory:")
        print(f"  RSS (Resident):      {proc_mem['rss_mb']:>8.2f} MB")
        print(f"  VMS (Virtual):       {proc_mem['vms_mb']:>8.2f} MB")
        print(f"  Usage:               {proc_mem['percent']:>8.2f}%")
        
        print(f"\n🖥️ System Memory:")
        print(f"  Total:               {sys_mem['total_mb']:>8.2f} MB")
        print(f"  Available:           {sys_mem['available_mb']:>8.2f} MB")
        print(f"  Used:                {sys_mem['used_mb']:>8.2f} MB")
        print(f"  Usage:               {sys_mem['percent']:>8.2f}%")
        
        print("\n" + "="*70 + "\n")
    
    @staticmethod
    def monitor_memory(func: Callable) -> Callable:
        """
        Decorator to monitor memory usage of a function
        
        Usage:
            @MemoryManager.monitor_memory
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Memory before
            mem_before = MemoryManager.get_memory_usage()
            
            # Run function
            result = func(*args, **kwargs)
            
            # Memory after
            mem_after = MemoryManager.get_memory_usage()
            
            # Calculate delta
            delta = mem_after['rss_mb'] - mem_before['rss_mb']
            
            logger.info(f"Memory: {func.__name__} used {delta:+.2f} MB")
            
            return result
        
        return wrapper
    
    @staticmethod
    def cleanup_after(func: Callable) -> Callable:
        """
        Decorator to force garbage collection after function
        
        Usage:
            @MemoryManager.cleanup_after
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            MemoryManager.force_gc()
            return result
        
        return wrapper


def batch_process(items: list, batch_size: int, process_func: Callable, cleanup: bool = True):
    """
    Process items in batches to limit memory usage
    
    Args:
        items: List of items to process
        batch_size: Number of items per batch
        process_func: Function to process each batch
        cleanup: Force GC after each batch
        
    Returns:
        List of results
    """
    results = []
    total_batches = (len(items) + batch_size - 1) // batch_size
    
    logger.info(f"Processing {len(items)} items in {total_batches} batches (size={batch_size})")
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)...")
        
        # Process batch
        batch_results = process_func(batch)
        results.extend(batch_results if isinstance(batch_results, list) else [batch_results])
        
        # Cleanup if requested
        if cleanup:
            gc.collect()
    
    logger.info(f"✅ Processed {len(items)} items in {total_batches} batches")
    
    return results


def optimize_dataframe_memory(df):
    """
    Optimize pandas DataFrame memory usage
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Optimized DataFrame
    """
    import pandas as pd
    
    # Get memory before
    mem_before = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # Optimize numeric columns
    for col in df.select_dtypes(include=['int']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    for col in df.select_dtypes(include=['float']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # Optimize object columns (strings)
    for col in df.select_dtypes(include=['object']).columns:
        num_unique = df[col].nunique()
        num_total = len(df[col])
        
        # Convert to category if < 50% unique values
        if num_unique / num_total < 0.5:
            df[col] = df[col].astype('category')
    
    # Get memory after
    mem_after = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    saved = mem_before - mem_after
    logger.info(f"DataFrame memory: {mem_before:.2f} MB → {mem_after:.2f} MB (saved {saved:.2f} MB)")
    
    return df


if __name__ == "__main__":
    # Test memory utilities
    print("="*70)
    print("MEMORY MANAGEMENT TEST")
    print("="*70)
    
    # Show current memory
    MemoryManager.print_memory_stats()
    
    # Test batch processing
    print("\n🧪 Testing batch processing...")
    
    def process_batch(batch):
        """Dummy batch processor"""
        return [x * 2 for x in batch]
    
    items = list(range(100))
    results = batch_process(items, batch_size=10, process_func=process_batch)
    
    print(f"✅ Processed {len(results)} items")
    
    # Test decorator
    print("\n🧪 Testing memory monitor decorator...")
    
    @MemoryManager.monitor_memory
    @MemoryManager.cleanup_after
    def test_function():
        # Create some data
        data = [i for i in range(1000000)]
        return len(data)
    
    result = test_function()
    print(f"✅ Function returned: {result}")
    
    # Show final memory
    MemoryManager.print_memory_stats()
    
    print("✅ Test completed!")
