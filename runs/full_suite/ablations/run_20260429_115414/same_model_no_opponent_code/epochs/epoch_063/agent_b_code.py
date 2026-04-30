def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Favor moving onto/near resources; avoid getting too close to opponent.
        if res:
            dres = min(man(nx, ny, rx, ry) for rx, ry in res)
        else:
            dres = 999999

        dop = man(nx, ny, ox, oy)
        # Prefer cells adjacent to resources (strong) but keep away from opponent.
        score = -2 * dres + (4 if dop >= 3 else -3 - dop)

        # Slightly prefer occupying positions that block opponent (adjacent to obstacles).
        if obstacles:
            adj_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    tx, ty = nx + ax, ny + ay
                    if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs:
                        adj_obs += 1
            score += adj_obs

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        # Deterministic fallback: try staying, else first valid move.
        if inside(sx, sy):
            return [0, 0]
        for dx, dy in moves[:-1]:
            if inside(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return best