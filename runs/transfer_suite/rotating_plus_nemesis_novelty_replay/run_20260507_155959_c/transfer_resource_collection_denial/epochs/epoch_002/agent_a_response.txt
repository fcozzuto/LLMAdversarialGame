def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        # Drift away from opponent if no resources are visible
        best = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = -md(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a resource where we aim to arrive first; also consider enemy "pressure".
    best_target = None
    best_tv = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        dsi = md(sx, sy, rx, ry)
        doi = md(ox, oy, rx, ry)
        # Negative is good (we're closer). Add slight bias toward closer overall.
        tv = (dsi - doi, dsi + 0.001 * (rx + ry))
        if best_target is None or tv < best_tv:
            best_target = (rx, ry)
            best_tv = tv

    tx, ty = best_target

    # If the opponent is strictly closer to our chosen target, switch to "deny":
    # move toward the resource where opponent advantage is smallest.
    dsi = md(sx, sy, tx, ty)
    doi = md(ox, oy, tx, ty)
    deny = (doi < dsi)
    if deny:
        best_target = None
        best_tv = None
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            dsi2 = md(sx, sy, rx, ry)
            doi2 = md(ox, oy, rx, ry)
            # minimize opponent advantage: (doi - dsi), then favor our closeness
            tv = (doi2 - dsi2, dsi2 + 0.001 * (rx + ry))
            if best_target is None or tv < best_tv:
                best_target = (rx, ry)
                best_tv = tv
        tx, ty = best_target

    # Pick move that most improves our competitive arrival score for the target.
    best = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dsn = md(nx, ny, tx, ty)
        don = md(ox, oy, tx, ty)
        # primary: reduce (dsn - don); secondary: reduce our distance; tertiary: reduce opponent reach to target
        v = (dsn - don, dsn, don)
        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]