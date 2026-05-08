def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))

    targets = unclaimed or resources or set()
    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1)]  # deterministic order (left, up, stay, right, down)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not targets:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = (abs(nx - ox) + abs(ny - oy), abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if best is None or score > best[0]:
                best = (score, [dx, dy])
        return best[1] if best is not None else [0, 0]

    best_move = [0, 0]
    best_val = None
    opp_dist_now = abs(sx - ox) + abs(sy - oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to_target = None
        for tx, ty in targets:
            d = abs(nx - tx) + abs(ny - ty)
            if d_to_target is None or d < d_to_target:
                d_to_target = d
        if d_to_target is None:
            d_to_target = 10**9
        opp_dist = abs(nx - ox) + abs(ny - oy)
        # Prefer closer to targets; break ties by moving away from opponent
        val = (-d_to_target, -(opp_dist - opp_dist_now), nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_val is not None else [0, 0]