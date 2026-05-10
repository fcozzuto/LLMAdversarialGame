def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target: prioritize resources where we are ahead; otherwise minimize opponent advantage.
    best = None
    best_key = None
    for tx, ty in res:
        self_d = cheb(sx, sy, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        ahead = self_d - opp_d
        # If both are equal, go for closer-to-us to reduce tie drift; deterministic tie by coord.
        key = (0 if ahead < 0 else 1, ahead, self_d, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    def step_options():
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    opts.append((0, 0))
                else:
                    opts.append((dx, dy))
        return opts

    # Greedy next move toward target with obstacle avoidance; tie-break by not moving away.
    best_move = (0, 0)
    best_score = None
    for dx, dy in step_options():
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_from = cheb(nx, ny, sx, sy)
        # Favor decreasing distance to target, and avoid excessive wandering.
        score = (d_to, -d_from, abs(dx), abs(dy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]