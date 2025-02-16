import os
import tempfile
import base64
import numpy as np
import tensorflow as tf
from io import BytesIO
from PIL import Image
from django.test import SimpleTestCase
from unittest.mock import patch
from model_loader import Classification

