def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = w - 1 - sx, h - 1 - sy
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = dist((nx, ny), (tx, ty))
            cand = (d, -dist((nx, ny), (ox, oy)))
            if best is None or cand < best[0]:
                best = (cand, (dx, dy))
        return [best[1][0], best[1][1]]

    def pick_target(px, py):
        best = None
        for rx, ry in resources:
            d_self = dist((px, py), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            if d_self <= d_opp:
                cand = (0, d_self, rx, ry)
            else:
                cand = (1, d_self - d_opp, d_self, -d_opp, rx, ry)
            if best is None or cand < best:
                best = cand
        return (best[2], best[3])  # (rx, ry)

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        tx, ty = pick_target(nx, ny)
        d_self = dist((nx, ny), (tx, ty))
        d_opp_to_target = dist((ox, oy), (tx, ty))
        # Prefer securing resources we can reach first; otherwise improve odds while moving away from opponent.
        can_secure = 0 if d_self <= d_opp_to_target else 1
        away = dist((nx, ny), (ox, oy))
        key = (can_secure, d_self, -away, d_opp_to_target, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]