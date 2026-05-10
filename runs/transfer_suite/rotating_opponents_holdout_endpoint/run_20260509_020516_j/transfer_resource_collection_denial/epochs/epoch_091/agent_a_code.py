def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_cell = None
    best_key = None
    for cell in resources:
        sd = mdist((sx, sy), cell)
        od = mdist((ox, oy), cell)
        # Prefer cells where we are already closer (race), then closer overall.
        key = (od - sd, -sd, cell[0], cell[1])
        if best_key is None or key > best_key:
            best_key = key
            best_cell = cell

    tx, ty = best_cell
    # Greedy step towards target with diagonal preference, but choose best legal among 8-neighborhood + stay.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # Evaluation for next position: capture if on resource, else improve our race vs opponent.
            capture = 1 if (nx, ny) == best_cell else 0
            sd = mdist((nx, ny), best_cell)
            od = mdist((ox, oy), best_cell)
            # Also mildly avoid stepping away from opponent's current sweep pattern: favor reducing y-distance if opponent is far in y.
            y_bias = -abs((ny - oy))
            key = (capture, od - sd, -sd, y_bias, -abs(dx) - abs(dy))
            candidates.append((key, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]