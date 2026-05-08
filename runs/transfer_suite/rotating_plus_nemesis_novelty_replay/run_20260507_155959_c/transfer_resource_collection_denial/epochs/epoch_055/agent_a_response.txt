def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    # Phase shift: early contest, late secure.
    # Early: chase the resource the opponent is most likely to reach first.
    # Late: ignore opponent and grab closest remaining to finish.
    late = turns_remaining <= 10
    target = None
    if late:
        best = None; bd = 10**9
        for rx, ry in res:
            d = md(sx, sy, rx, ry)
            if d < bd or (d == bd and (rx, ry) < best):
                bd = d; best = (rx, ry)
        target = best
    else:
        # Choose resource maximizing (opp_dist - self_dist): easiest steal.
        best = None; best_key = None
        for rx, ry in res:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            key = (od - sd, -sd, rx, ry)  # deterministic: prefer higher steal gap, then nearer, then lexicographic
            if best_key is None or key > best_key:
                best_key = key; best = (rx, ry)
        target = best

    tx, ty = target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Greedy step toward target with opponent-aware tie-break
    best_m = None; best_key = None
    for dx, dy, nx, ny in moves:
        dself = md(nx, ny, tx, ty)
        dopp = md(nx, ny, ox, oy)  # indirect pressure: keep some separation from opponent
        # tie-break favors staying closer to opponent when stealing is possible, else go faster to target
        steal_bias = md(ox, oy, tx, ty) - dself
        key = (-dself, -steal_bias, opp_d := dself, -dopp, dx, dy)
        if best_key is None or key > best_key:
            best_key = key; best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]