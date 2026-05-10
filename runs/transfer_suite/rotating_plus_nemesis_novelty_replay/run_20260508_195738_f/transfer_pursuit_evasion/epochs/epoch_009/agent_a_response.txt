def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_step(target_dx, target_dy):
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            tx = nx - (nx - target_dx)
            ty = ny - (ny - target_dy)
            v = max(abs(nx - ox), abs(ny - oy))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return best if best is not None else (0, 0)

    self_role = observation.get("self_role", "")
    is_pursuer = "purs" in str(self_role).lower()

    if is_pursuer:
        # Greedy chase with obstacle avoidance
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = max(abs(nx - ox), abs(ny - oy))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Evade: maximize distance from pursuer, with a corner bias to avoid oscillation
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Choose corner deterministically based on current positions
    idx = (sx + 3 * sy + ox + 5 * oy + observation.get("turn_index", 0)) % 4
    corner = corners[idx]

    best = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = max(abs(nx - ox), abs(ny - oy))
        corner_dist = abs(nx - corner[0]) + abs(ny - corner[1])
        v = (dist, corner_dist)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]