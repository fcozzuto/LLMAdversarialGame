def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1]) if len(sp) > 1 else (int(sp[0]), 0)
    ox, oy = int(op[0]), int(op[1]) if len(op) > 1 else (int(op[0]), 0)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obs.add((bx, by))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    role = str(observation.get("self_role", "")).lower()
    evader = "evader" in role

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        v = dist2(nx, ny)
        if evader:
            key = v
        else:
            key = -v
        if best is None or key > best_val:
            best_val = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]