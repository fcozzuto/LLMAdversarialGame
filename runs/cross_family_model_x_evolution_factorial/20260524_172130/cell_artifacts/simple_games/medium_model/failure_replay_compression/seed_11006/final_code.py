def choose_move(observation):
    # Defensive accessors for position
    pos = observation.get("position", {})
    x = pos.get("x", 0)
    y = pos.get("y", 0)

    # Collect potential targets from common fields
    targets = []
    for key in ("resources", "targets", "goals", "points", "items"):
        area = observation.get(key, [])
        if isinstance(area, list):
            for t in area:
                if isinstance(t, dict):
                    tx = t.get("x")
                    ty = t.get("y")
                    if tx is not None and ty is not None:
                        targets.append((tx, ty))

    # If we have targets, head toward the nearest one using Chebyshev-like step
    if targets:
        best = None
        best_dist = None
        for tx, ty in targets:
            dx = tx - x
            dy = ty - y
            dist = max(abs(dx), abs(dy))  # lattice distance suitable for grid moves
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best = (dx, dy)
        if best is not None:
            dx, dy = best
            dx = 0 if dx == 0 else (1 if dx > 0 else -1)
            dy = 0 if dy == 0 else (1 if dy > 0 else -1)
            return [dx, dy]

    # Fallback: move toward the center (0,0) to stay robust
    dx = 0
    dy = 0
    dx = 0 if x == 0 else (1 if x > 0 else -1)
    dy = 0 if y == 0 else (1 if y > 0 else -1)

    # Clip defensively
    dx = -1 if dx < -1 else (1 if dx > 1 else dx)
    dy = -1 if dy < -1 else (1 if dy > 1 else dy)

    return [dx, dy]
