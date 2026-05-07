def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def steps(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonals allowed)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    # If opponent sweeps rows, prioritize crossing rows away from their current y
    # while still beating their estimated arrival time to a resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        immediate = 1 if (nx, ny) in set(res) else 0

        val = immediate * 1000
        if res:
            opp_row_factor = 1 if ny != oy else 0
            for (rx, ry) in res:
                s = steps(nx, ny, rx, ry)
                o = steps(ox, oy, rx, ry)
                margin = (o - s)
                if margin < 0:
                    continue
                # prefer resources that we can reach before opponent, especially when we move off opponent's row
                row_bonus = opp_row_factor * (1 if ry != oy else 0)
                # small deterministic tie-break: bias toward closer resources if margins equal
                val += margin * 10 + row_bonus * 3 - s
        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best