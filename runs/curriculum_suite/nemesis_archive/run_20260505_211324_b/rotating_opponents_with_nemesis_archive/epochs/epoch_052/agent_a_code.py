def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        best = min(moves, key=lambda t: (md(t[2], t[3], ox, oy), t[0], t[1]))
        return [int(best[0]), int(best[1])]

    # pick a target resource: closest to us, tie by deterministic order
    target = min(res, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))

    # score moves: go closer to target; avoid moving into opponent advantage
    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        d_me = md(nx, ny, target[0], target[1])
        d_opp = md(ox, oy, target[0], target[1])
        # prioritize reducing our distance; if opponent is closer, slightly bias away
        score = d_me * 10 + (0 if d_me <= d_opp else 3) + abs(nx - ox) * 0 + abs(ny - oy) * 0
        score = (score, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]