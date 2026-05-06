def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

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
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        score = 0
        for tx, ty in res:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)

            if myd == 0:
                score += 10**6
                continue
            # Prefer resources where we arrive strictly earlier, but also avoid bad contests.
            if myd < opd:
                gap = opd - myd
                score += 120 * gap - 3 * myd
            elif myd == opd:
                score -= 80 + 2 * myd
            else:
                score -= 35 + 2 * myd

            # Slightly reward reducing our distance to resources we are likely contesting.
            myd0 = md(sx, sy, tx, ty)
            if myd < myd0:
                score += 6
            else:
                score -= 1

        # Tie-break deterministically by preferring moves closer to best target direction.
        if best is None:
            best = (dx, dy)
            best_score = score
        else:
            if score > best_score:
                best_score = score
                best = (dx, dy)
            elif score == best_score:
                if (dx, dy) < best:
                    best = (dx, dy)

    return [best[0], best[1]]