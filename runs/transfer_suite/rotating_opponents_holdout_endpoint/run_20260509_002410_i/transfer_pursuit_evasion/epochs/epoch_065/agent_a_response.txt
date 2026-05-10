def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = observation.get("self_role", "pursuer")
    is_pursuer = (self_role == "pursuer")

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))

    if not candidates:
        candidates = [(dx, dy, sx + dx, sy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    # Tie-break deterministically: prefer smallest dx then smallest dy, with role-appropriate objective.
    best = None
    if is_pursuer:
        # Minimize distance to opponent.
        for dx, dy, nx, ny in candidates:
            score = dist2(nx, ny, ox, oy)
            key = (score, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
    else:
        # Maximize distance from opponent.
        for dx, dy, nx, ny in candidates:
            score = dist2(nx, ny, ox, oy)
            key = (-score, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)

    return [int(best[1]), int(best[2])]