def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0
    if not (0 <= ox < w and 0 <= oy < h):
        ox, oy = 0, 0

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def adj_obs(x, y):
        c = 0
        for tx, ty in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + tx, y + ty) in obs:
                c += 1
        return c

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Assume opponent moves next to maximize distance from us while avoiding obstacles.
        worst_escape = -1
        best_opp = None
        for odx, ody in deltas:
            mx, my = ox + odx, oy + ody
            if not legal(mx, my):
                continue
            esc = manh(nx, ny, mx, my) * 100 + adj_obs(mx, my) * 2
            if esc > worst_escape:
                worst_escape = esc
                best_opp = (mx, my)
        if best_opp is None:
            best_opp = (ox, oy)
            worst_escape = manh(nx, ny, ox, oy) * 100

        tx, ty = best_opp
        # Primary: minimize our distance to opponent after their best response.
        d = manh(nx, ny, tx, ty)
        # Secondary: prefer stepping into "thinner" routes (near obstacles) while not stuck.
        risk = adj_obs(nx, ny)
        tie = (d, risk, abs(dx) + abs(dy))
        score = d * 1000 + risk * 3 + (0.01 if (nx == tx and ny == ty) else 0.0)
        if score < best[0] or (score == best[0] and tie < (best[1], best[2], 0)):
            best = (score, dx, dy)

    return [best[1] if best[1] in (-1, 0, 1) else 0, best[2] if best[2] in (-1, 0, 1) else 0]