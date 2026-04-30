def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obstacles]
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Opponent likely target: closest resource to opponent (deterministic tie-break).
    op_t = min(res, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        # Primary: maximize advantage over all resources (opp_dist - my_dist).
        adv = max((cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry), -cheb(nx, ny, rx, ry), -(rx + 8 * ry))
                  for (rx, ry) in res)
        # Secondary: actively contest opponent's likely target.
        tx, ty = op_t
        myd_t = cheb(nx, ny, tx, ty)
        opd_t = cheb(ox, oy, tx, ty)
        score = adv[0] * 1000 - myd_t + 0.01 * (opd_t)
        # Deterministic tie-break: prefer staying, then smaller dx, then smaller dy.
        tie = (0 if (dx == 0 and dy == 0) else 1, dx, dy)
        if best_score is None or (score, tie) > (best