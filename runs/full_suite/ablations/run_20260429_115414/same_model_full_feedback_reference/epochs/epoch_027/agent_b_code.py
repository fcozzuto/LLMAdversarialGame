def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))
    if not res:
        res = [((W - 1) // 2, (H - 1) // 2)]
        if res[0] in obs:
            res = [(0, 0)]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            score = 0
            # Prefer moving to resource where we are much closer than the opponent.
            # Deterministic tie-break: smaller distance to self, then smaller opponent distance, then stable dx/dy order.
            local_best = None
            for rx, ry in res:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Higher is better: being closer than opponent
                s = (do - ds) * 1000 - ds
                cand = (s, ds, do, rx, ry)
                if local_best is None or cand > local_best:
                    local_best = cand
            score = local_best[0]
            tieb = local_best[1:4]
        else:
            # If no resources, just chase toward opponent
            ds_to_o = man(nx, ny, ox, oy)
            score = -ds_to_o
            tieb = (ds_to_o, 0, 0)
        key = (score, tieb)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]