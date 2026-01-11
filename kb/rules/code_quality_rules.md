# Code Quality Rules

**Priority:** High
**Applies To:** All coding agents
**Last Updated:** 2025-10-22
**Updated By:** System

## Rules

1. **Testing Requirements**
   - Write unit tests for all new functions
   - Achieve at least 80% code coverage
   - Run tests before committing code
   - Include both positive and negative test cases

2. **Code Documentation**
   - Add docstrings to all functions and classes
   - Include parameter types and return values
   - Provide usage examples where appropriate
   - Keep comments up-to-date with code changes

3. **Security Practices**
   - Never commit secrets or API keys
   - Validate all user inputs
   - Use parameterized queries for database operations
   - Keep dependencies updated

4. **Code Review**
   - All code must be reviewed before merging
   - Address all review comments
   - Ensure CI/CD pipeline passes
   - Update documentation as needed

## Examples

### Good Example:
```python
def calculate_total(items: list[float], tax_rate: float = 0.1) -> float:
    """
    Calculate total price including tax.
    
    Args:
        items: List of item prices
        tax_rate: Tax rate as decimal (default: 0.1 for 10%)
    
    Returns:
        Total price including tax
    
    Example:
        >>> calculate_total([10.0, 20.0], 0.1)
        33.0
    """
    subtotal = sum(items)
    return subtotal * (1 + tax_rate)
```
