def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                targets.append((x, y))
    recent = set()
    for p in (observation.get("self_path") or [])[-6:]:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                recent.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if targets:
            d = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        else:
            d = abs(nx - cx) + abs(ny - cy)
        t_bonus = 0
        if (nx, ny) in self_t:
            t_bonus -= 2
        if (nx, ny) in opp_t:
            t_bonus += 1
        loop_pen = 1 if (nx, ny) in recent else 0
        key = (loop_pen, d, t_bonus, dx, dy)
        if best_key is None or key < best_key:
            best_key, best = key, [dx, dy]
    return best if best is not None else [0, 0]