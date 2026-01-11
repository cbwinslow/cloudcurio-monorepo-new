# Robust Toolset Implementation Guide

This guide provides practical implementation details for building robust, reliable toolsets for podcast production agents.

## Implementation Strategy

### 1. **Core Implementation Principles**

```python
# Focus on practical, working implementations
class PracticalToolImplementation:
    """Base class for practical tool implementations."""

    def __init__(self, config=None):
        self.config = config or {}
        self.logger = self._setup_logging()
        self.metrics = self._initialize_metrics()

    def _setup_logging(self):
        """Setup comprehensive logging."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(f'logs/{self.__class__.__name__}.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

        return logger

    def _initialize_metrics(self):
        """Initialize performance metrics."""
        return {
            'execution_count': 0,
            'success_count': 0,
            'failure_count': 0,
            'avg_execution_time': 0,
            'last_execution_time': 0
        }
```

### 2. **Practical Error Handling**

```python
def _handle_errors_practically(self, error: Exception, context: Dict) -> Any:
    """Handle errors with practical recovery strategies."""

    error_type = type(error).__name__

    # Log the error with context
    self.logger.error(f"Error in {context.get('tool_name', 'unknown')}: {str(error)}")
    self.logger.debug(f"Error context: {context}")

    # Practical error handling strategies
    if isinstance(error, FileNotFoundError):
        return self._handle_missing_file(error, context)

    elif isinstance(error, ValueError):
        return self._handle_invalid_input(error, context)

    elif isinstance(error, MemoryError):
        return self._handle_memory_error(error, context)

    elif isinstance(error, TimeoutError):
        return self._handle_timeout(error, context)

    else:
        return self._handle_generic_error(error, context)
```

### 3. **Resource Management**

```python
def _manage_resources_practically(self, operation: str, resource_type: str) -> bool:
    """Manage resources with practical limits."""

    # Check resource availability
    if resource_type == 'memory':
        memory_info = psutil.virtual_memory()
        if memory_info.percent > 85:
            self.logger.warning(f"High memory usage: {memory_info.percent}%")
            return False

    elif resource_type == 'cpu':
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 90:
            self.logger.warning(f"High CPU usage: {cpu_percent}%")
            return False

    elif resource_type == 'disk':
        disk_info = psutil.disk_usage('/')
        if disk_info.percent > 95:
            self.logger.warning(f"High disk usage: {disk_info.percent}%")
            return False

    # Resource is available
    return True
```

## Practical Tool Implementations

### 1. **Video Analysis Tool**

```python
class PracticalVideoAnalysisTool(PracticalToolImplementation):
    """Practical video analysis implementation."""

    def analyze_video(self, video_path: str, analysis_type: str = 'full') -> Dict:
        """Analyze video with practical error handling."""

        # Validate input
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if analysis_type not in ['speaker_detection', 'engagement', 'cut_points', 'full']:
            raise ValueError(f"Invalid analysis type: {analysis_type}")

        # Check resources
        if not self._manage_resources_practically('video_analysis', 'memory'):
            raise ResourceError("Insufficient memory for video analysis")

        try:
            # Load video
            video = self._load_video_safely(video_path)

            # Perform analysis
            if analysis_type == 'speaker_detection':
                result = self._detect_speakers_practically(video)
            elif analysis_type == 'engagement':
                result = self._analyze_engagement_practically(video)
            elif analysis_type == 'cut_points':
                result = self._find_cut_points_practically(video)
            else:  # full analysis
                result = {
                    'speakers': self._detect_speakers_practically(video),
                    'engagement': self._analyze_engagement_practically(video),
                    'cut_points': self._find_cut_points_practically(video)
                }

            # Validate result
            self._validate_analysis_result(result, analysis_type)

            return {
                'success': True,
                'data': result,
                'analysis_type': analysis_type,
                'video_path': video_path
            }

        except Exception as e:
            return self._handle_errors_practically(e, {
                'tool_name': 'video_analysis',
                'video_path': video_path,
                'analysis_type': analysis_type
            })

    def _load_video_safely(self, video_path: str) -> Any:
        """Load video with practical error handling."""

        try:
            # Try multiple video loading methods
            for loader in [self._try_ffmpeg_loader, self._try_opencv_loader, self._try_pillow_loader]:
                try:
                    video = loader(video_path)
                    if video is not None:
                        return video
                except Exception:
                    continue

            raise RuntimeError("All video loading methods failed")

        except Exception as e:
            self.logger.error(f"Failed to load video {video_path}: {str(e)}")
            raise

    def _detect_speakers_practically(self, video: Any) -> List[Dict]:
        """Detect speakers with practical approach."""

        # Use multiple detection methods
        methods = [
            self._detect_speakers_face_recognition,
            self._detect_speakers_audio_analysis,
            self._detect_speakers_motion_detection
        ]

        results = []
        for method in methods:
            try:
                method_results = method(video)
                if method_results:
                    results.extend(method_results)
            except Exception as e:
                self.logger.warning(f"Speaker detection method failed: {str(e)}")

        # Deduplicate and merge results
        return self._merge_speaker_results(results)
```

### 2. **Audio Processing Tool**

```python
class PracticalAudioProcessingTool(PracticalToolImplementation):
    """Practical audio processing implementation."""

    def process_audio(self, audio_path: str, output_path: str, processing_steps: List[str] = None) -> Dict:
        """Process audio with practical error handling."""

        # Validate inputs
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if processing_steps is None:
            processing_steps = ['noise_reduction', 'de_essing', 'equalization']

        # Check output directory
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            # Load audio
            audio = self._load_audio_safely(audio_path)

            # Apply processing steps
            processed_audio = audio
            for step in processing_steps:
                processed_audio = self._apply_processing_step(processed_audio, step)

            # Save result
            self._save_audio_safely(processed_audio, output_path)

            return {
                'success': True,
                'input_path': audio_path,
                'output_path': output_path,
                'processing_steps': processing_steps,
                'file_size': os.path.getsize(output_path)
            }

        except Exception as e:
            return self._handle_errors_practically(e, {
                'tool_name': 'audio_processing',
                'audio_path': audio_path,
                'output_path': output_path,
                'processing_steps': processing_steps
            })

    def _apply_processing_step(self, audio: Any, step: str) -> Any:
        """Apply single processing step with fallback."""

        step_methods = {
            'noise_reduction': [
                self._apply_noise_reduction_ffmpeg,
                self._apply_noise_reduction_pydub,
                self._apply_noise_reduction_manual
            ],
            'de_essing': [
                self._apply_de_essing_ffmpeg,
                self._apply_de_essing_manual
            ],
            'equalization': [
                self._apply_equalization_ffmpeg,
                self._apply_equalization_manual
            ]
        }

        if step not in step_methods:
            self.logger.warning(f"Unknown processing step: {step}")
            return audio

        # Try each method until one succeeds
        for method in step_methods[step]:
            try:
                result = method(audio)
                if result is not None:
                    return result
            except Exception as e:
                self.logger.warning(f"Processing method failed for {step}: {str(e)}")

        # All methods failed
        self.logger.error(f"All processing methods failed for step: {step}")
        return audio
```

### 3. **Content Scheduling Tool**

```python
class PracticalContentSchedulingTool(PracticalToolImplementation):
    """Practical content scheduling implementation."""

    def schedule_content(self, content: str, platforms: List[str], schedule_time: str = None) -> Dict:
        """Schedule content with practical error handling."""

        # Validate inputs
        if not content or len(content.strip()) == 0:
            raise ValueError("Content cannot be empty")

        if not platforms or len(platforms) == 0:
            raise ValueError("At least one platform must be specified")

        # Validate platforms
        valid_platforms = ['twitter', 'instagram', 'tiktok', 'youtube', 'linkedin']
        for platform in platforms:
            if platform not in valid_platforms:
                raise ValueError(f"Invalid platform: {platform}")

        try:
            results = {}

            # Process each platform
            for platform in platforms:
                platform_result = self._schedule_to_platform(
                    content, platform, schedule_time
                )
                results[platform] = platform_result

            return {
                'success': True,
                'content': content,
                'platforms': platforms,
                'schedule_time': schedule_time,
                'results': results
            }

        except Exception as e:
            return self._handle_errors_practically(e, {
                'tool_name': 'content_scheduling',
                'content': content,
                'platforms': platforms,
                'schedule_time': schedule_time
            })

    def _schedule_to_platform(self, content: str, platform: str, schedule_time: str = None) -> Dict:
        """Schedule to specific platform with multiple methods."""

        platform_methods = {
            'twitter': [
                self._schedule_twitter_api_v2,
                self._schedule_twitter_api_v1,
                self._schedule_twitter_web_interface
            ],
            'instagram': [
                self._schedule_instagram_api,
                self._schedule_instagram_web_interface
            ],
            'tiktok': [
                self._schedule_tiktok_api,
                self._schedule_tiktok_web_interface
            ],
            'youtube': [
                self._schedule_youtube_api,
                self._schedule_youtube_web_interface
            ],
            'linkedin': [
                self._schedule_linkedin_api,
                self._schedule_linkedin_web_interface
            ]
        }

        if platform not in platform_methods:
            return {'status': 'error', 'error': f'Unknown platform: {platform}'}

        # Try each scheduling method
        for method in platform_methods[platform]:
            try:
                result = method(content, schedule_time)
                if result.get('status') == 'success':
                    return result
            except Exception as e:
                self.logger.warning(f"Scheduling method failed for {platform}: {str(e)}")

        # All methods failed
        return {
            'status': 'error',
            'error': f'All scheduling methods failed for {platform}',
            'content': content
        }
```

## Integration Patterns

### 1. **Agent Integration**

```python
class PracticalVideoEditorAgent:
    """Practical video editor agent implementation."""

    def __init__(self):
        self.tools = {
            'video_analysis': PracticalVideoAnalysisTool(),
            'auto_cut': PracticalAutoCutTool(),
            'add_overlays': PracticalAddOverlaysTool()
        }
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute_workflow(self, workflow_name: str, inputs: Dict) -> Dict:
        """Execute workflow with practical error handling."""

        try:
            if workflow_name == 'episode_edit':
                return self._execute_episode_edit_workflow(inputs)
            elif workflow_name == 'short_creation':
                return self._execute_short_creation_workflow(inputs)
            else:
                raise ValueError(f"Unknown workflow: {workflow_name}")

        except Exception as e:
            self.logger.error(f"Workflow {workflow_name} failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'workflow': workflow_name,
                'inputs': inputs
            }

    def _execute_episode_edit_workflow(self, inputs: Dict) -> Dict:
        """Execute episode edit workflow with practical steps."""

        results = {}

        # Step 1: Video analysis with fallback
        analysis_result = self._execute_with_fallback(
            'video_analysis',
            {'video_path': inputs['video_path'], 'analysis_type': 'full'},
            fallback_strategies=['reduce_quality', 'segment_processing']
        )

        if not analysis_result.get('success'):
            return analysis_result

        results['analysis'] = analysis_result

        # Step 2: Auto cutting with fallback
        cut_result = self._execute_with_fallback(
            'auto_cut',
            {
                'video_path': inputs['video_path'],
                'cut_points': analysis_result['data']['cut_points']
            },
            fallback_strategies=['reduce_quality', 'alternative_algorithm']
        )

        if not cut_result.get('success'):
            return cut_result

        results['cut_video'] = cut_result

        # Step 3: Add overlays with fallback
        overlay_result = self._execute_with_fallback(
            'add_overlays',
            {
                'video_path': cut_result['data']['output_path'],
                'overlays': inputs.get('overlays', [])
            },
            fallback_strategies=['reduce_quality', 'segment_processing']
        )

        if not overlay_result.get('success'):
            return overlay_result

        results['final_video'] = overlay_result

        return {
            'success': True,
            'results': results,
            'workflow': 'episode_edit',
            'quality_score': self._calculate_workflow_quality(results)
        }

    def _execute_with_fallback(self, tool_name: str, parameters: Dict, fallback_strategies: List[str]) -> Dict:
        """Execute tool with practical fallback strategies."""

        if tool_name not in self.tools:
            return {'success': False, 'error': f'Unknown tool: {tool_name}'}

        # Try primary execution
        try:
            result = self.tools[tool_name].execute(parameters)
            if result.get('success'):
                return result
        except Exception as e:
            self.logger.warning(f"Primary execution failed for {tool_name}: {str(e)}")

        # Try fallback strategies
        for strategy in fallback_strategies:
            try:
                fallback_result = self._apply_fallback_strategy(
                    tool_name, parameters, strategy
                )
                if fallback_result.get('success'):
                    self.logger.info(f"Fallback strategy {strategy} succeeded for {tool_name}")
                    return fallback_result
            except Exception as e:
                self.logger.warning(f"Fallback strategy {strategy} failed for {tool_name}: {str(e)}")

        # All strategies failed
        return {
            'success': False,
            'error': f'All execution strategies failed for {tool_name}',
            'tool_name': tool_name,
            'parameters': parameters
        }
```

### 2. **Workflow Orchestration**

```python
class PracticalWorkflowOrchestrator:
    """Practical workflow orchestrator implementation."""

    def __init__(self):
        self.agents = {
            'video_editor': PracticalVideoEditorAgent(),
            'audio_engineer': PracticalAudioEngineerAgent(),
            'social_media': PracticalSocialMediaAgent()
        }
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = self._initialize_metrics()

    def execute_production_workflow(self, inputs: Dict) -> Dict:
        """Execute complete production workflow with practical steps."""

        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()

        self.logger.info(f"Starting production workflow {workflow_id}")

        results = {}

        try:
            # Step 1: Video editing
            video_result = self._execute_agent_with_retry(
                'video_editor',
                'episode_edit',
                {
                    'video_path': inputs['video_path'],
                    'overlays': inputs.get('overlays', [])
                },
                max_retries=2
            )

            if not video_result.get('success'):
                return self._handle_workflow_failure(workflow_id, 'video_editing', video_result)

            results['video'] = video_result

            # Step 2: Audio processing
            audio_result = self._execute_agent_with_retry(
                'audio_engineer',
                'audio_mastering',
                {
                    'audio_path': inputs['audio_path'],
                    'video_cut_points': video_result['results']['analysis']['data']['cut_points']
                },
                max_retries=2
            )

            if not audio_result.get('success'):
                return self._handle_workflow_failure(workflow_id, 'audio_processing', audio_result)

            results['audio'] = audio_result

            # Step 3: Social media scheduling
            social_result = self._execute_agent_with_retry(
                'social_media',
                'content_scheduling',
                {
                    'content': inputs['social_content'],
                    'platforms': inputs.get('platforms', ['twitter', 'instagram']),
                    'media_path': video_result['results']['final_video']['data']['output_path']
                },
                max_retries=3
            )

            if not social_result.get('success'):
                return self._handle_workflow_failure(workflow_id, 'social_scheduling', social_result)

            results['social'] = social_result

            # Calculate overall quality
            overall_quality = self._calculate_overall_quality(results)

            # Update metrics
            self._update_metrics(workflow_id, start_time, True, overall_quality)

            return {
                'success': True,
                'workflow_id': workflow_id,
                'results': results,
                'quality_score': overall_quality,
                'execution_time': (datetime.now() - start_time).total_seconds(),
                'status': 'Production complete'
            }

        except Exception as e:
            self._update_metrics(workflow_id, start_time, False, 0.0)
            return self._handle_workflow_failure(workflow_id, 'orchestration', {'error': str(e)})

    def _execute_agent_with_retry(self, agent_name: str, workflow_name: str, inputs: Dict, max_retries: int = 2) -> Dict:
        """Execute agent workflow with practical retry logic."""

        if agent_name not in self.agents:
            return {'success': False, 'error': f'Unknown agent: {agent_name}'}

        last_error = None

        for attempt in range(max_retries + 1):
            try:
                result = self.agents[agent_name].execute_workflow(workflow_name, inputs)

                # Check if result indicates partial success that can be recovered
                if not result.get('success') but self._can_recover_from_error(result):
                    self.logger.warning(f"Attempt {attempt + 1} failed but recoverable: {result.get('error')}")
                    last_error = result
                    continue

                return result

            except Exception as e:
                last_error = {'success': False, 'error': str(e)}
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

                if attempt < max_retries:
                    # Exponential backoff
                    sleep_time = 2 ** attempt
                    self.logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)

        # All attempts failed
        return last_error or {'success': False, 'error': 'All execution attempts failed'}

    def _can_recover_from_error(self, result: Dict) -> bool:
        """Determine if error is recoverable."""

        error = result.get('error', '')

        # List of recoverable error patterns
        recoverable_errors = [
            'temporary',
            'timeout',
            'rate limit',
            'resource',
            'connection',
            'network'
        ]

        # Check if error contains recoverable patterns
        error_lower = error.lower()
        return any(pattern in error_lower for pattern in recoverable_errors)
```

## Testing Strategy

### 1. **Unit Testing**

```python
class TestPracticalVideoAnalysis(unittest.TestCase):
    """Practical unit tests for video analysis."""

    def setUp(self):
        self.tool = PracticalVideoAnalysisTool()
        self.test_video = 'tests/test_video.mp4'

    def test_successful_analysis(self):
        """Test successful video analysis."""

        # Create test video file
        self._create_test_video(self.test_video)

        result = self.tool.analyze_video(self.test_video, 'speaker_detection')

        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIsInstance(result['data'], list)

        # Clean up
        os.remove(self.test_video)

    def test_missing_file(self):
        """Test handling of missing video file."""

        result = self.tool.analyze_video('nonexistent.mp4', 'speaker_detection')

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('not found', result['error'].lower())

    def test_invalid_analysis_type(self):
        """Test handling of invalid analysis type."""

        # Create test video file
        self._create_test_video(self.test_video)

        result = self.tool.analyze_video(self.test_video, 'invalid_type')

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('invalid', result['error'].lower())

        # Clean up
        os.remove(self.test_video)

    def test_resource_limitation(self):
        """Test handling of resource limitations."""

        # Mock resource limitation
        with patch.object(self.tool, '_manage_resources_practically', return_value=False):
            result = self.tool.analyze_video(self.test_video, 'speaker_detection')

            self.assertFalse(result['success'])
            self.assertIn('error', result)
            self.assertIn('resource', result['error'].lower())
```

### 2. **Integration Testing**

```python
class TestPracticalWorkflowIntegration(unittest.TestCase):
    """Practical integration tests for workflows."""

    def setUp(self):
        self.orchestrator = PracticalWorkflowOrchestrator()

    def test_complete_workflow_success(self):
        """Test complete workflow with successful execution."""

        inputs = {
            'video_path': 'tests/test_video.mp4',
            'audio_path': 'tests/test_audio.mp3',
            'social_content': 'Test social media content',
            'platforms': ['twitter', 'instagram']
        }

        # Mock agent results
        with patch.object(self.orchestrator.agents['video_editor'], 'execute_workflow') as mock_video, \
             patch.object(self.orchestrator.agents['audio_engineer'], 'execute_workflow') as mock_audio, \
             patch.object(self.orchestrator.agents['social_media'], 'execute_workflow') as mock_social:

            mock_video.return_value = {'success': True, 'results': {'analysis': {'data': {'cut_points': []}}}}
            mock_audio.return_value = {'success': True}
            mock_social.return_value = {'success': True}

            result = self.orchestrator.execute_production_workflow(inputs)

            self.assertTrue(result['success'])
            self.assertIn('video', result['results'])
            self.assertIn('audio', result['results'])
            self.assertIn('social', result['results'])

    def test_workflow_with_retry(self):
        """Test workflow with retry on recoverable errors."""

        inputs = {
            'video_path': 'tests/test_video.mp4',
            'audio_path': 'tests/test_audio.mp3',
            'social_content': 'Test social media content'
        }

        # Mock agent results with initial failure then success
        with patch.object(self.orchestrator.agents['video_editor'], 'execute_workflow') as mock_video:

            # First call fails, second succeeds
            mock_video.side_effect = [
                {'success': False, 'error': 'Temporary network issue'},
                {'success': True, 'results': {'analysis': {'data': {'cut_points': []}}}}
            ]

            result = self.orchestrator.execute_production_workflow(inputs)

            self.assertTrue(result['success'])
            self.assertEqual(mock_video.call_count, 2)
```

## Deployment Strategy

### 1. **Configuration Management**

```python
class PracticalConfigurationManager:
    """Practical configuration management."""

    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = self._load_configuration()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _load_configuration(self) -> Dict:
        """Load configuration with practical error handling."""

        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)

            # Validate configuration
            self._validate_configuration(config)

            return config

        except FileNotFoundError:
            self.logger.warning(f"Configuration file {self.config_file} not found, using defaults")
            return self._get_default_configuration()

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in configuration file: {str(e)}")
            return self._get_default_configuration()

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return self._get_default_configuration()

    def _validate_configuration(self, config: Dict) -> None:
        """Validate configuration with practical checks."""

        # Check required sections
        required_sections = ['tools', 'agents', 'resources']
        for section in required_sections:
            if section not in config:
                self.logger.warning(f"Missing configuration section: {section}")
                config[section] = {}

        # Validate tool configurations
        if 'tools' in config:
            for tool_name, tool_config in config['tools'].items():
                if not isinstance(tool_config, dict):
                    self.logger.warning(f"Invalid tool configuration for {tool_name}")
                    config['tools'][tool_name] = {}
```

### 2. **Monitoring and Logging**

```python
class PracticalMonitoringSystem:
    """Practical monitoring and logging system."""

    def __init__(self):
        self.logger = self._setup_comprehensive_logging()
        self.metrics = self._initialize_comprehensive_metrics()
        self.alert_thresholds = {
            'error_rate': 0.1,  # 10% error rate
            'execution_time': 300,  # 5 minutes
            'resource_usage': 0.8  # 80% resource usage
        }

    def _setup_comprehensive_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""

        logger = logging.getLogger('PracticalMonitoring')
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        # File handler for detailed logs
        file_handler = logging.FileHandler('logs/monitoring_detailed.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d'
        ))

        # Error file handler
        error_handler = logging.FileHandler('logs/monitoring_errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - ERROR - %(name)s - %(message)s - %(exc_info)s'
        ))

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

        return logger

    def monitor_execution(self, execution_id: str, tool_name: str, start_time: float, success: bool, error: str = None) -> None:
        """Monitor tool execution with practical metrics."""

        execution_time = time.time() - start_time

        # Update metrics
        self.metrics['total_executions'] += 1
        self.metrics['execution_times'].append(execution_time)

        if success:
            self.metrics['success_count'] += 1
        else:
            self.metrics['failure_count'] += 1
            self.logger.error(f"Execution {execution_id} failed: {error}")

        # Check for alerts
        self._check_for_alerts()

        # Log execution details
        log_level = logging.INFO if success else logging.ERROR
        self.logger.log(log_level, f"Execution {execution_id} - {tool_name} - {'SUCCESS' if success else 'FAILED'} - {execution_time:.2f}s")

    def _check_for_alerts(self) -> None:
        """Check for alert conditions."""

        # Calculate error rate
        total = self.metrics['total_executions']
        if total > 0:
            error_rate = self.metrics['failure_count'] / total
            if error_rate > self.alert_thresholds['error_rate']:
                self._trigger_alert('high_error_rate', f"Error rate {error_rate:.2%} exceeds threshold")

        # Check average execution time
        if self.metrics['execution_times']:
            avg_time = sum(self.metrics['execution_times']) / len(self.metrics['execution_times'])
            if avg_time > self.alert_thresholds['execution_time']:
                self._trigger_alert('slow_execution', f"Average execution time {avg_time:.2f}s exceeds threshold")

        # Check resource usage
        self._check_resource_usage()

    def _trigger_alert(self, alert_type: str, message: str) -> None:
        """Trigger alert with practical notification methods."""

        alert_message = f"ALERT: {alert_type} - {message}"

        # Log alert
        self.logger.error(alert_message)

        # Email notification (if configured)
        if hasattr(self, 'email_config'):
            self._send_email_alert(alert_message)

        # Slack notification (if configured)
        if hasattr(self, 'slack_config'):
            self._send_slack_alert(alert_message)

        # Add to alert history
        self.metrics['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'message': message
        })
```

## Best Practices Summary

### 1. **Practical Implementation**

- Focus on functionality that works in real scenarios
- Implement reasonable error handling and recovery
- Use practical resource management

### 2. **Comprehensive Testing**

- Test both success and failure scenarios
- Include edge cases and error conditions
- Validate integration between components

### 3. **Robust Monitoring**

- Monitor execution metrics and resource usage
- Implement practical alerting systems
- Maintain comprehensive logs

### 4. **Clear Documentation**

- Document practical usage examples
- Include troubleshooting guidance
- Provide clear error messages

### 5. **Continuous Improvement**

- Monitor tool performance in production
- Collect feedback from real usage
- Iteratively improve based on practical experience

## Implementation Checklist

- [ ] Base tool framework with practical error handling
- [ ] Input validation with clear error messages
- [ ] Resource management with practical limits
- [ ] Quality assessment and scoring
- [ ] Fallback strategies for error recovery
- [ ] Performance metrics and monitoring
- [ ] Comprehensive testing suite
- [ ] Clear documentation and examples
- [ ] Integration with agent framework
- [ ] Workflow orchestration capabilities
- [ ] Configuration management
- [ ] Deployment and monitoring systems

This implementation guide provides a practical approach to building robust, reliable toolsets that work effectively in real-world podcast production scenarios.
