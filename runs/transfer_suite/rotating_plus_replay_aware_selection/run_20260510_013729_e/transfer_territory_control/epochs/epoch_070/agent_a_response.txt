def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    if not unclaimed:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    self_t = observation.get("self_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)

    def edge_bonus(x, y):
        return 1.2 if (x == 0 or x == w - 1 or y == 0 or y == h - 1) else 0.0

    # Choose an unclaimed target we can reach earlier than the opponent.
    best = None
    best_score = -10**9
    for tx, ty in unclaimed:
        if (tx, ty) in obs:
            continue
        d_s = dist((sx, sy), (tx, ty))
        d_o = dist((ox, oy), (tx, ty))
        if d_s == 0:
            adv = 2.0
        else:
            adv = (d_o - d_s)
        adj = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (tx + dx, ty + dy) in self_set:
                    adj = 1
                    break
            if adj:
                break
        score = 2.0 * adv - 0.35 * d_s + 0.9 * adj + edge_bonus(tx, ty)
        if score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_d = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = dist((nx, ny), (tx, ty))
        if d < best_d:
            best_d = d
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]