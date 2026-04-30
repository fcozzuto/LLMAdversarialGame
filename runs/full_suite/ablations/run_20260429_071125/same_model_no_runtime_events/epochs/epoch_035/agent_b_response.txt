def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Deterministic fallback: move toward center while staying valid.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move, best_d, dirs = [0, 0], 10**9, [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = king_dist(nx, ny, cx, cy)
            if d < best_d or (d == best_d and (dx, dy) < tuple(best_move)):
                best_d, best_move = d, [dx, dy]
        return best_move

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick the resource with best capture advantage (opponent farther than us).
    best_t = None
    best_adv = -10**18
    best_ds = 10**18
    for rx, ry in resources:
        ds = king_dist(sx, sy, rx, ry)
        do = king_dist(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (rx, ry) < best_t))):
            best_adv, best_ds, best_t = adv, ds, (rx, ry)

    tx, ty = best_t

    # Choose move maximizing (opponent_dist - new_self_dist), tie-break by smaller new_self_dist.
    op_to_t = king_dist(ox, oy, tx, ty)
    best_move = [0, 0]
    best_val = -10**18
    best_new_ds = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        new_ds = king_dist(nx, ny, tx, ty)
        val = op_to_t - new_ds
        if val > best_val or (val == best_val and (new_ds < best_new_ds or (new_ds == best_new_ds and (dx, dy) < tuple(best_move)))):
            best_val, best_new_ds, best_move = val, new_ds, [dx, dy]

    return best_move