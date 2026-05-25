"""
Auto Shorts Generator - Main Entry Point
Generates AI-powered YouTube Shorts automatically
"""

import sys
import argparse
from src.pipeline import ShortsGenerationPipeline

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Auto Shorts Generator - Create YouTube Shorts automatically'
    )
    
    parser.add_argument(
        '--generate',
        type=int,
        default=1,
        help='Number of shorts to generate (default: 1)'
    )
    
    parser.add_argument(
        '--upload',
        action='store_true',
        help='Upload generated shorts to YouTube'
    )
    
    parser.add_argument(
        '--topic',
        type=str,
        default=None,
        help='Specific topic for shorts (uses random if not specified)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show pipeline statistics'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        pipeline = ShortsGenerationPipeline()
        
        # Generate shorts
        if args.generate > 0:
            if args.generate == 1:
                # Single short
                pipeline.generate_short(topic=args.topic, upload=args.upload)
            else:
                # Batch
                pipeline.generate_batch(count=args.generate, upload=args.upload)
        
        # Show stats
        if args.stats or args.generate > 0:
            pipeline.print_stats()
        
        print("\n✅ All done!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
