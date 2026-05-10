def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation.get("opponent_position", (x, y))
    obstacles = observation.get("obstacles", [])
    obs = set(tuple(p) for p in obstacles) if obstacles is not None else set()

    def cheb(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    targets = observation.get("unclaimed_cells")
    if not targets:
        targets = observation.get("resources")
    if targets is None:
        targets = []
    tg = [tuple(p) for p in targets]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0); bestv = -10**9

    opp = (ox, oy)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        pos = (nx, ny)
        v = 0
        if tg:
            dmin = min(cheb(pos, t) for t in tg)
            v += 1000 - 20 * dmin
            # small anti-opponent pressure: prefer targets that opponent is farther from
            dopp = min(cheb(opp, t) for t in tg)
            v += (dopp - dmin)
        else:
            v += 5 * (cheb(opp, pos) - cheb(pos, opp))  # tie-break toward opponent
            v += -cheb(pos, (w // 2, h // 2))

        if v > bestv:
            bestv = v; best = (dx, dy)

    return [best[0], best[1]]