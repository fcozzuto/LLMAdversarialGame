def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role", "")).lower()
    is_evader = "evader" in role

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not ok(sx, sy):
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))

    dirs = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        val = dist if is_evader else -dist
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]