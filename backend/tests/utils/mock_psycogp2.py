import sys
from unittest.mock import MagicMock

# Create a MagicMock object to mock psycopg2
mock_psycopg2 = MagicMock()
sys.modules['psycopg2'] = mock_psycopg2
sys.modules['psycopg2.extras'] = mock_psycopg2.extras
sys.modules['psycopg2.extensions'] = mock_psycopg2.extensions

