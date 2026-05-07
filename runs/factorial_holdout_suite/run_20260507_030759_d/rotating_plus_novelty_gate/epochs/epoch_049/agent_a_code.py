def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)

    obstacles = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources") or []
    resources = set((r[0], r[1]) for r in resources)

    if (sx, sy) in resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            score = md(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d1 = md(nx, ny, rx, ry)
            if d1 < my_best:
                my_best = d1
            d2 = md(ox, oy, rx, ry)
            if d2 < opp_best:
                opp_best = d2
        # Prefer moves that get closer to resources and, secondarily, farther from opponent.
        score = (-my_best, md(nx, ny, ox, oy) - opp_best)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]