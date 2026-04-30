def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def occ(x, y):
        return 1 if (x, y) in obst else 0

    if not resources:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if occ(nx, ny):
            continue

        # Primary: improve our race vs opponent on resources.
        our_min_adv = 10**18
        opp_min_adv = -10**18
        for rx, ry in resources:
            if occ(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Want ds small relative to do => maximize (do - ds)
            val = do - ds
            if val < our_min_adv:
                our_min_adv = val
            if val > opp_min_adv:
                opp_min_adv = val

        # Secondary: reduce our distance to the best reachable resource.
        best_ds = 10**18
        for rx, ry in resources:
            if occ(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            if ds < best_ds:
                best_ds = ds

        # Tertiary: avoid obstacle proximity (smoother paths).
        near = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                x2, y2 = nx + ddx, ny + ddy
                if (x2, y2) in obst:
                    near += 1

        # Combine: prioritize race advantage, then pickup speed, then obstacle safety.
        val = our_min_adv * 1000 + (0 if best_ds == 10**18 else -best_ds) * 10 - near
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move