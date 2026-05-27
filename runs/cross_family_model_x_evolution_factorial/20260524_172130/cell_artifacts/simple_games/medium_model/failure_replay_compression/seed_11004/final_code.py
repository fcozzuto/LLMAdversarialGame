def choose_move(observation):
    obs = observation or {}
    grid = obs.get("grid", []) or []
    height = obs.get("height", len(grid)) if grid else obs.get("height", 0)
    width = obs.get("width", len(grid[0]) if grid and grid[0] else 0) if grid else obs.get("width", 0)

    pos = obs.get("position", {}) or {}
    x = pos.get("x", width // 2 if width else 0)
    y = pos.get("y", height // 2 if height else 0)

    def in_bounds(nx, ny):
        if ny < 0 or nx < 0:
            return False
        if not grid:
            return False
        return ny < len(grid) and nx < len(grid[ny])

    def is_target(nx, ny, kind):
        if not in_bounds(nx, ny):
            return False
        return grid[ny][nx] == kind

    # Priority 1: resource
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if is_target(nx, ny, "resource"):
                return [dx, dy]

    # Priority 2: evade enemy if adjacent
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if is_target(nx, ny, "enemy"):
                away_dx = -dx
                away_dy = -dy
                away_dx = max(-1, min(1, away_dx))
                away_dy = max(-1, min(1, away_dy))
                if away_dx != 0 or away_dy != 0:
                    return [away_dx, away_dy]

    # Priority 3: move toward center to stabilize
    if width and height:
        center_dx = 0
        center_dy = 0
        if x > width // 2:
            center_dx = -1
        elif x < width // 2:
            center_dx = 1
        if y > height // 2:
            center_dy = -1
        elif y < height // 2:
            center_dy = 1
        if center_dx != 0 or center_dy != 0:
            return [center_dx, center_dy]

    # Fallback: move right
    return [1, 0]
