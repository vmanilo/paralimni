import pytest
from unittest.mock import AsyncMock, patch
from services.bittensor import Bittensor


@pytest.mark.asyncio
async def test_get_dividends_cache_hit(mocker):
    """
    Test when the dividend is found in the cache.
    """
    # Arrange
    cache = AsyncMock()
    cache.get_dividend.return_value = 100  # Simulate cache hit

    chain = AsyncMock()
    chain.get_dividend.return_value = None  # Chain should not be consulted

    # Mock the Bittensor dependencies
    mocker.patch("services.bittensor.CacheHandler", return_value=cache)
    mocker.patch("services.bittensor.ChainHandler", return_value=chain)

    bittensor = Bittensor('', '', 1)

    # Act
    result, from_cache = await bittensor.get_dividend(netuid=1, hotkey="key123")

    # Assert
    assert result == 100  # Dividend correctly retrieved from cache
    assert from_cache is True

    cache.get_dividend.assert_called_once_with(1, "key123")  # Cache accessed
    chain.get_dividend.assert_not_called()  # Chain not accessed


@pytest.mark.asyncio
async def test_get_dividends_cache_miss_chain_hit(mocker):
    """
    Test when the dividend is not in the cache but found in the chain.
    """
    # Arrange
    cache = AsyncMock()
    cache.get_dividend.return_value = None  # Simulate cache miss
    cache.store_dividend = AsyncMock()  # Mock storing afterwards

    chain = AsyncMock()
    chain.get_dividend.return_value = 200  # Simulate chain hit

    # Mock the Bittensor dependencies
    mocker.patch("services.bittensor.CacheHandler", return_value=cache)
    mocker.patch("services.bittensor.ChainHandler", return_value=chain)

    bittensor = Bittensor('', '', 1)

    # Act
    result, from_cache = await bittensor.get_dividend(netuid=2, hotkey="key456")

    # Assert
    assert result == 200  # Dividend retrieved from the chain
    assert from_cache is False

    cache.get_dividend.assert_called_once_with(2, "key456")  # Cache accessed
    chain.get_dividend.assert_called_once_with(2, "key456")  # Chain accessed
    cache.store_dividend.assert_called_once_with(2, "key456", 200)  # Cached after retrieval


@pytest.mark.asyncio
async def test_get_dividends_cache_miss_chain_miss(mocker):
    """
    Test when the dividend is not found in both the cache and the chain.
    """
    # Arrange
    cache = AsyncMock()
    cache.get_dividend.return_value = None  # Simulate cache miss

    chain = AsyncMock()
    chain.get_dividend.return_value = None  # Simulate chain miss

    # Mock the Bittensor dependencies
    mocker.patch("services.bittensor.CacheHandler", return_value=cache)
    mocker.patch("services.bittensor.ChainHandler", return_value=chain)

    bittensor = Bittensor('', '', 1)

    # Act
    result, from_cache = await bittensor.get_dividend(netuid=3, hotkey="key789")

    # Assert
    assert result is None  # Dividend not found
    assert from_cache is False

    cache.get_dividend.assert_called_once_with(3, "key789")  # Cache accessed
    chain.get_dividend.assert_called_once_with(3, "key789")  # Chain accessed
    cache.store_dividend.assert_not_called()  # Nothing stored in cache


@pytest.mark.asyncio
async def test_store_dividend_called_on_chain_hit(mocker):
    """
    Test that store_dividend is called to cache the value when it's retrieved from the chain.
    """
    # Arrange
    cache = AsyncMock()
    cache.get_dividend.return_value = None  # Simulate cache miss
    cache.store_dividend = AsyncMock()

    chain = AsyncMock()
    chain.get_dividend.return_value = 300  # Simulate chain hit

    # Mock Bittensor dependencies
    mocker.patch("services.bittensor.CacheHandler", return_value=cache)
    mocker.patch("services.bittensor.ChainHandler", return_value=chain)

    bittensor = Bittensor('', '', 1)

    # Act
    await bittensor.get_dividend(netuid=4, hotkey="key999")

    # Assert
    cache.store_dividend.assert_called_once_with(4, "key999", 300)  # Dividend stored
