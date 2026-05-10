def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []
    score_map = set(map(tuple, observation.get("scores") or [])) if observation.get("scores") is not None else set()

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def sgn(a):
        return (a > 0) - (a < 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    opp_adj = []
    for x, y in opp_t:
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                opp_adj.append((nx, ny))
    targets = opp_adj[:]
    if not targets:
        for r in resources:
            try:
                rx, ry = r
            except Exception:
                continue
            if inside(rx, ry) and (rx, ry) not in obstacles:
                targets.append((rx, ry))
    if not targets:
        targets = [c for c in unclaimed if inside(c[0], c[1]) and c not in obstacles]
    if not targets:
        targets = [(sx, sy)]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best = None
    best_sc = -10**30
    for tx, ty in targets:
        if (tx, ty) in obstacles:
            continue
        adj = 1 if (tx, ty) in opp_adj else 0
        if (tx, ty) in score_map:
            rb = 50
        else:
            rb = 0
        sc = adj * 10000 + rb * 10 - dist2(sx, sy, tx, ty) - dist2(ox, oy, tx, ty) // 3
        if sc > best_sc or (sc == best_sc and (tx, ty) < best):
            best_sc = sc
            best = (tx, ty)
    tx, ty = best

    chosen = (0, 0)
    chosen_sc = -10**30
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = -dist2(nx, ny, tx, ty) - dist2(nx, ny, ox, oy) // 3
        if (nx, ny) in unclaimed:
            sc += 2000
            if (nx, ny) in opp_adj:
                sc += 3000
        if sc > chosen_sc or (sc == chosen_sc and (dx, dy) < chosen):
            chosen_sc = sc
            chosen = (dx, dy)
    return [int(chosen[0]), int(chosen[1])]