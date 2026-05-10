def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_t.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def adj(c1, c2):
        return max(abs(c1[0] - c2[0]), abs(c1[1] - c2[1])) == 1

    frontier = []
    if self_t and unclaimed:
        for u in unclaimed:
            if any(adj(u, t) for t in self_t):
                frontier.append(u)

    targets = frontier if frontier else unclaimed
    if not targets:
        # Fall back to resources if no unclaimed known
        res = []
        for p in observation.get("resources") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                res.append((int(p[0]), int(p[1])))
        targets = res if res else [((w - 1) // 2, (h - 1) // 2)]

    # Score targets: prefer closer, then closer to opponent (deny), deterministic tie-breaker
    best = None
    best_key = None
    for t in targets:
        tx, ty = t
        if (tx, ty) in obs:
            continue
        key = (abs(tx - x) + abs(ty - y), -(abs(tx - ox) + abs(ty - oy)), ty, tx)
        if best_key is None or key < best_key:
            best_key = key
            best = t
    if best is None:
        return [0, 0]

    tx, ty = best
    dx_dir = 0 if tx == x else (1 if tx > x else -1)
    dy_dir = 0 if ty == y else (1 if ty > y else -1)

    candidates = [(dx_dir, dy_dir), (dx_dir, 0), (0, dy_dir), (0, 0)]
    # Also allow diagonal variants if closer than pure axis step
    if dx_dir != 0 and dy_dir != 0:
        candidates = [(dx_dir, dy_dir), (dx_dir, 0), (0, dy_dir), (dx_dir, -dy_dir), (-dx_dir, dy_dir), (0, 0)]

    best_move = (0, 0)
    best_dist = None
    for dx, dy in candidates:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if best_dist is None or d < best_dist or (d == best_dist and (dy, dx) < (best_move[1], best_move[0])):
            best_dist = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]