def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_advantage(nx, ny):
        # Prefer resources where we can reach earlier than opponent; break ties by smaller our distance.
        best = None
        # Deterministic resource order
        res = sorted((r[0], r[1]) for r in resources)
        for rx, ry in res:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d
            key = (adv, -our_d, -rx, -ry)  # maximize adv, then minimize our_d, then deterministic
            if best is None or key > best[0]:
                best = (key, our_d)
        return best[0] if best is not None else None

    if not resources:
        # Drift away from opponent, favor staying off obstacles; deterministic tie-break to center.
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dist_opp = cheb(nx, ny, ox, oy)
            dist_ctr = cheb(nx, ny, cx, cy)
            key = (dist_opp, -dist_ctr, -nx, -ny)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        if best is None:
            return [0, 0]
        return [best[1][0], best[1][1]]

    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        k = best_resource_advantage(nx, ny)
        if k is None:
            continue
        # Small preference to move (avoid getting stuck) while keeping determinism via tie-break.
        move_bonus = - (0 if dx == 0 and dy == 0 else 1)
        key = (k[0], k[1], move_bonus, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]