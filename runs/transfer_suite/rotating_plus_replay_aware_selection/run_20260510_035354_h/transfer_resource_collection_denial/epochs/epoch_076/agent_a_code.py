def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cd(a, b):  # Chebyshev distance (diagonal movement)
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in moves:
        best_key = None
        for rx, ry in res:
            sd = cd((nx, ny), (rx, ry))
            od = cd((ox, oy), (rx, ry))
            # Prefer resources where we can beat opponent; add urgency and deterministic tie-break.
            key = (od - sd, -sd, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
        # Slight preference for moving toward the current best target (not just beating by distance).
        k = (best_key[0], best_key[1], -abs(nx - sx) - abs(ny - sy), best_key[2], best_key[3], dx, dy)
        if best is None or k > best:
            best = k
            best_move = [dx, dy]

    return best_move