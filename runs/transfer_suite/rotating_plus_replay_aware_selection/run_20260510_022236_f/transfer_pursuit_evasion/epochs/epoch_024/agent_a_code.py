def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    def edge_dist(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    best_score = None
    best_move = [0, 0]
    # Deterministic tie-break order by fixed move list and secondary criteria.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        fn = free_neighbors(nx, ny)
        ed = edge_dist(nx, ny)
        if is_evader:
            # Prefer larger distance, avoid stepping into tight spaces, and lightly avoid edges.
            score = (d, fn, -ed)
            better = best_score is None or score > best_score
        else:
            # Prefer smaller distance, and avoid stepping into tight spaces (dead-ends).
            score = (-d, fn, -ed)
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]