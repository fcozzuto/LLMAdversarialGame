def choose_move(observation):
    # Defensive defaults
    x = observation.get("x", 0)
    y = observation.get("y", 0)
    width = observation.get("width", 0)
    height = observation.get("height", 0)
    # Try to use a simple robust strategy that works across tasks:
    # Move away from nearest threat if present; otherwise seek center.
    # Look for common keys
    grid = observation.get("grid", None)
    threats = []
    if grid is not None:
        try:
            # grid is expected as a 2D list of strings
            for i, row in enumerate(grid):
                for j, cell in enumerate(row):
                    if isinstance(cell, str) and ("enemy" in cell or "threat" in cell or "obstacle" in cell):
                        threats.append((i, j))
        except Exception:
            threats = []
    # Compute a vector away from threats near us
    dx, dy = 0, 0
    if threats:
        # find closest threat to our position (x,y)
        best = None
        for tx, ty in threats:
            dist = (tx - y)**2 + (ty - x)**2
            if best is None or dist < best[0]:
                best = (dist, tx, ty)
        if best:
            tx, ty = best[1], best[2]
            # direction away
            dy = -1 if ty > y else (1 if ty < y else 0)
            dx = -1 if tx > x else (1 if tx < x else 0)
            # clamp to -1,0,1
            dx = max(-1, min(1, dx))
            dy = max(-1, min(1, dy))
            if dx == 0 and dy == 0:
                dx, dy = -1, 0
            return [dx, dy]
    # If no threats, a simple objective: move toward center if possible
    cx, cy = 0, 0
    if width and height:
        cx = width // 2
        cy = height // 2
        dx = -1 if x > cx else (1 if x < cx else 0)
        dy = -1 if y > cy else (1 if y < cy else 0)
        dx = max(-1, min(1, dx))
        dy = max(-1, min(1, dy))
        if dx == 0 and dy == 0:
            dx, dy = 0, 1
        return [dx, dy]
    # Fallback: small random-looking but deterministic pattern
    if (x + y) % 2 == 0:
        return [1, 0]
    else:
        return [0, 1]
