def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def deg_free(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    def step_score(nx, ny):
        d = max(abs(ox - nx), abs(oy - ny))  # capture radius 0
        center_bias = abs(cx - nx) + abs(cy - ny)  # farther from center = "cornerier"
        free = deg_free(nx, ny)
        # obstacle proximity: penalize cells adjacent to many obstacles
        adj_obs = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if inb(tx, ty) and (tx, ty) in obstacles:
                adj_obs += 1
        # prefer staying away from trap-ish clutter when evading; prefer open lanes when pursuing
        if self_is_pursuer:
            return (-d * 10.0) + (free * 0.6) - (adj_obs * 0.8) - (center_bias * 0.05)
        else:
            return (d * 10.0) + (center_bias * 0.8) + (free * 0.2) - (adj_obs * 0.9)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = step_score(nx, ny)
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]