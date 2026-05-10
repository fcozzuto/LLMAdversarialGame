def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w)
    h = int(h)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                resources.append((x, y))

    if not resources:
        resources = [((sx + ox) // 2, (sy + oy) // 2)]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        min_dist_to_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        val = -(min_dist_to_res * 10) + (dist_to_opp * 2)
        # If near opponent, slightly prefer moving away to avoid contact
        if dist_to_opp <= 2:
            val += dist_to_opp * 8
        if val > best_score:
            best_score = val
            best = [dx, dy]

    if best is None:
        # Fallback: deterministic safe-ish step
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best