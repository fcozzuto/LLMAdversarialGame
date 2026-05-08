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

    def md(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_key = None
        for rx, ry in res:
            dself = md((sx, sy), (rx, ry))
            dopp = md((ox, oy), (rx, ry))
            gap = dopp - dself  # positive => we can reach earlier
            # Prefer stealable, then closer, then slightly earlier in game.
            key = (gap, -dself, -(turns_remaining - 0))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

        # If opponent is closer to everything, switch to a contesting target:
        if all(md((ox, oy), r) <= md((sx, sy), r) for r in res):
            # pick resource closest to opponent (most urgent), with tie-break favoring staying near it
            urgent = min(res, key=lambda r: (md((ox, oy), r), md((sx, sy), r)))
            tx, ty = urgent

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    bestm = (0, 0); bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = md((nx, ny), (tx, ty))
        # small tie-break: move to reduce opponent's advantage by getting nearer to target
        v2 = md((ox, oy), (tx, ty)) - md((nx, ny), (tx, ty))
        # obstacle-adjacent penalty
        adj_pen = 0
        for ax in (-1,0,1):
            for ay in (-1,0,1):
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in obs:
                    adj_pen += 1
        score = (v, -v2, adj_pen)
        if bestv is None or score < bestv:
            bestv = score; bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]