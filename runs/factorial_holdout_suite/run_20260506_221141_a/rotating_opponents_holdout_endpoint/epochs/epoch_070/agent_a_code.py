def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for diagonal movement

    # If standing on a resource, stay to ensure collection
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    time_left = int(observation.get("turns_remaining", 0) or 0)
    aggressiveness = 1.0 + (20 - time_left) / 80.0  # earlier: race resources; later: be slightly more selective
    if aggressiveness < 0.85: aggressiveness = 0.85
    if aggressiveness > 1.3: aggressiveness = 1.3

    best = None
    best_key = None
    for i, (rx, ry) in enumerate(resources):
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources where we are closer; penalize those where opponent is closer.
        score = sd - aggressiveness * od
        # Tie-break deterministically: smaller sd, then smaller od, then lexical.
        key = (score, sd, od, rx, ry, i)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    # If the next cell is blocked, try axis-aligned fallback toward target
    if (nx, ny) in obstacles:
        options = []
        if dx != 0:
            options.append((dx, 0))
        if dy != 0:
            options.append((0, dy))
        options.append((0, 0))
        for adx, ady in options:
            cx, cy = sx + adx, sy + ady
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles:
                return [int(adx), int(ady)]
        return [0, 0]

    return [int(dx), int(dy)]