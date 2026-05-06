def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist8(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    best = None
    best_key = None
    for r in resources:
        dm = dist8((sx, sy), r)
        do = dist8((ox, oy), r)
        # Prefer resources where we arrive earlier; also avoid opponent row to reduce contention.
        row_avoid = 1 if r[1] != oy else 0
        steal_bias = do - dm
        # Break ties deterministically by coordinates.
        key = (steal_bias, row_avoid, -dm, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best
    dx = tx - sx
    dy = ty - sy

    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    nx, ny = sx + step_x, sy + step_y

    if (nx, ny) in obstacles:
        # Try axis-aligned alternatives deterministically.
        candidates = [(step_x, 0), (0, step_y), (0, 0)]
        for cx, cy in candidates:
            ex, ey = sx + cx, sy + cy
            if 0 <= ex < w and 0 <= ey < h and (ex, ey) not in obstacles:
                return [int(cx), int(cy)]
        return [0, 0]

    # Ensure within bounds (engine would keep in place, but keep deterministic).
    if 0 <= nx < w and 0 <= ny < h:
        return [int(step_x), int(step_y)]
    # If out of bounds, clamp deterministically by trying valid moves.
    candidates = [(step_x, step_y), (step_x, 0), (0, step_y), (0, 0)]
    for cx, cy in candidates:
        ex, ey = sx + cx, sy + cy
        if 0 <= ex < w and 0 <= ey < h and (ex, ey) not in obstacles:
            return [int(cx), int(cy)]
    return [0, 0]