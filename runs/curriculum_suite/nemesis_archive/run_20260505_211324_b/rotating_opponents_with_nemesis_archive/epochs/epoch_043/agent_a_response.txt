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
    if not res:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Choose a target that we are likely to secure (prefer where opponent is farther).
    best_targets = []
    for tx, ty in res:
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Encourage (opponent_distance - self_distance); discourage being too far overall.
        score = (opd - myd) * 6 - myd * 0.7
        # If we are already at/near it, boost strongly.
        score += 25 if (tx, ty) == (sx, sy) else 0
        score += 5 if myd <= 2 and opd > myd else 0
        best_targets.append((score, tx, ty))
    best_targets.sort(key=lambda t: (-(t[0]), t[1], t[2]))
    _, tx, ty = best_targets[0]

    # Pick move that maximizes expected advantage toward (tx,ty), considering nearby resources too.
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (sx, sy) == (tx, ty):
        # Try to stay but still look for a better neighboring target.
        pass

    def advantage(px, py):
        # Sum a few strongest local advantages deterministically.
        vals = []
        for rx, ry in res:
            myd = md(px, py, rx, ry)
            opd = md(ox, oy, rx, ry)
            vals.append((opd - myd) * 4 - myd * 0.4 + (18 if (rx, ry) == (px, py) else 0))
        vals.sort(reverse=True)
        k = 3 if len(vals) >= 3 else len(vals)
        return sum(vals[:k])

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        myd_next = md(nx, ny, tx, ty)
        myd_now = md(sx, sy, tx, ty)
        # Prefer reducing distance to main target; break ties by advantage.
        val = (myd_now - myd_next) * 10 + advantage(nx, ny) - myd_next * 0.3
        # Deterministic tie-break.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]