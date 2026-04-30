def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def near_obs_pen(x, y):
        pen = 0
        for ax in (x - 1, x, x + 1):
            for ay in (y - 1, y, y + 1):
                if (ax, ay) in obstacles:
                    pen += 2
        return pen

    def score_target(tx, ty):
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Prefer resources we're closer to; also prefer closer-in general.
        return (opd - myd) * 5 - myd - near_obs_pen(tx, ty)

    # Pick target where we have a relative advantage; if none, fall back to closest resource.
    target = None
    best = None
    for tx, ty in resources:
        val = score_target(tx, ty)
        if best is None or val > best:
            best = val
            target = (tx, ty)
    if target is None:
        target = (ox, oy)

    tx, ty = target
    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        myd = md(nx, ny, tx, ty)
        opd = md(nx, ny, ox, oy)
        cur_my = md(sx, sy, tx, ty)
        cur_opd = md(sx, sy, ox, oy)

        # Greedy improvement: reduce distance to target; if target is gone, chase opponent.
        improve_target = (cur_my - myd) * 6
        improve_opponent = (cur_opd - opd) * 2

        # Avoid stepping into tight obstacle areas; and avoid moving adjacent to opponent if not helping target.
        risk = near_obs_pen(nx, ny)
        opp_adj = 1 if abs(nx - ox) <= 1 and abs(ny - oy) <= 1 else 0
        opp_term = (opp_adj * 5) if improve_target <= 0 else (opp_adj * 1)

        val = improve_target + improve_opponent - risk - opp_term - (md(nx, ny, tx, ty) > 12) * 3
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]