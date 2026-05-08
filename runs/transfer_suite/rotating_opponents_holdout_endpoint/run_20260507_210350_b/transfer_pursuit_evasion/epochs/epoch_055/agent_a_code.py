def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evader" in role_self) or ("runner" in role_self)
    opp_is_evader = ("evader" in role_opp) or ("runner" in role_opp)

    resources = observation.get("resources", []) or []
    if resources:
        res = []
        for p in resources:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obstacles:
                    res.append((x, y))
        resources = res

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            closest = min(md(nx, ny, rx, ry) for rx, ry in resources)
            val = closest
        else:
            d = md(nx, ny, ox, oy)
            val = -d if self_is_evader else d  # evader runs away, pursuer approaches/captures

        # Deterministic tie-break: prefer smaller val; then prefer not staying; then lexicographic dx,dy
        key = (val, 1 if (dx, dy) == (0, 0) else 0, dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move