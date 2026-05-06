def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in moves:
        best_for_cell = -10**18
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            gain = od - sd  # positive means we are closer
            # Deny more aggressively when opponent is closer.
            if gain >= 0:
                val = gain * 60 - sd * 2
            else:
                val = gain * 25 - sd * 1 - (od * 0.5)
            # Slight tie-break: prefer progressing away from current position less.
            val -= (abs(nx - sx) + abs(ny - sy)) * 0.01
            if val > best_for_cell:
                best_for_cell = val
        if best is None or best_for_cell > best[0]:
            best = (best_for_cell, dx, dy)
    return [int(best[1]), int(best[2])]