#!/usr/bin/env python3
"""
Test script to capture full bot startup output
"""
import sys
import os
import logging

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_debug.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    logger.info("=" * 70)
    logger.info("STARTING BOT TEST")
    logger.info("=" * 70)
    
    # Add project root to path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    logger.info(f"Project root: {project_root}")
    logger.info(f"Python path: {sys.path[:3]}")
    
    # Import main after path setup
    logger.info("Importing main module...")
    import src.main as main_module
    
    logger.info("Main module imported successfully")
    logger.info(f"FastAPI app created: {main_module.app}")
    
    # Try to run app
    logger.info("Starting uvicorn server...")
    import uvicorn
    
    uvicorn.run(
        main_module.app,
        host="0.0.0.0",
        port=8080,
        log_level="debug"
    )
    
except KeyboardInterrupt:
    logger.info("\n[INFO] Bot stopped by user")
except Exception as e:
    logger.error(f"[ERROR] {e}", exc_info=True)
    import traceback
    traceback.print_exc()
