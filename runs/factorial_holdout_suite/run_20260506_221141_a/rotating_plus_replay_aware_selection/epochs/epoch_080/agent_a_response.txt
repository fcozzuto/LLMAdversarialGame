def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir movement

    def best_target():
        best = None
        best_key = (-10**18, 10**18)  # (advantage, my_dist)
        for rx, ry in resources:
            dm = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - dm  # higher means we are closer
            key = (adv, dm)
            if key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        # deterministic corner drift
        tx, ty = (gw - 1, gh - 1) if (sx + sy) <= (gw - 1 + gh - 1 - (sx + sy)) else (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny) and (dist(nx, ny, tx, ty) == min(dist(sx + mx, sy + my, tx, ty) for mx, my in [m for m in moves if legal(sx + m[0], sy + m[1])])):
                return [dx, dy]
        return [0, 0]

    rx, ry = target
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dm_next = dist(nx, ny, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer moves that keep/extend advantage, then reduce distance, then avoid opponent proximity slightly.
        adv = do - dm_next
        val = adv * 100 - dm_next
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move