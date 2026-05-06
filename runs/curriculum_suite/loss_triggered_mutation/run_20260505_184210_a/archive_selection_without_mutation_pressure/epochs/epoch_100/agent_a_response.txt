def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))
    res_set = set(resources)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if (sx, sy) in res_set:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = 0
            if (nx, ny) in res_set:
                v += 10**6
            v -= 0.05 * md(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = legal[0]
    bestv = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue

        # nearest resource distance (Manhattan)
        nr = 10**9
        tie2 = 10**9
        if resources:
            for rx, ry in resources:
                d = md(nx, ny, rx, ry)
                if d < nr:
                    nr = d
                    tie2 = md(nx, ny, ox, oy)
                elif d == nr:
                    # prefer keeping opponent farther among equal resource distances
                    t = md(nx, ny, ox, oy)
                    if t < tie2:
                        tie2 = t

        # heuristic:
        # - primary: minimize distance to resources
        # - secondary: maximize distance from opponent (safer + less contest)
        # - tertiary: prefer staying aligned with opponent's direction to intercept indirectly
        dopp = md(nx, ny, ox, oy)
        v = 0
        if (nx, ny) in res_set:
            v -= 10**6
        v += nr * 10.0
        v -= dopp * 0.8
        v += (md(nx, ny, sx, sy) * 0.02)  # slight discouragement of oscillation

        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]