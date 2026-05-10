def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res_raw = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    resources = [(p[0], p[1]) for p in res_raw if p and len(p) >= 2]
    obstacles = {(p[0], p[1]) for p in obs_raw if p and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def near_obstacle_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, ox, oy) - 0.5 * near_obstacle_pen(nx, ny)
            if v > best[1]:
                best = ((dx, dy), v)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        n_pen = near_obstacle_pen(nx, ny)
        # Race heuristic: prefer states where we are earlier to some resource than the opponent.
        # Deterministic aggregate: take best advantage among resources, with a small preference for closeness.
        best_adv = -10**18
        for rx, ry in resources:
            st = cheb(nx, ny, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            adv = (ot - st) * 2 - st  # earlier is strongly better; closer still matters
            if adv > best_adv:
                best_adv = adv
        # Additional bias: if we're on a resource, strongly commit.
        on_res_bonus = 200 if (nx, ny) in set(resources) else 0
        val = best_adv + on_res_bonus - 0.35 * n_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If all candidate moves were invalid due to obstacles/out-of-bounds, stay.
    return [int(best_move[0]), int(best_move[1])]