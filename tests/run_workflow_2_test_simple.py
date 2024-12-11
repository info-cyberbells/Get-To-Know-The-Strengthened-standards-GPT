import asyncio
import logging
from test_workflow_2 import setup_components, test_workflow_2_real_world_scenario

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        # Get components
        components = setup_components()
        
        # Run the test
        await test_workflow_2_real_world_scenario(components)
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
