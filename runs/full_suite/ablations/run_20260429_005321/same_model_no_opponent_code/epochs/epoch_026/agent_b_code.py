def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(a, b, c, d):
        d1 = a - c
        if d1 < 0: d1 = -d1
        d2 = b - d
        if d2 < 0: d2 = -d2
        return d1 + d2

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rt = (r[0], r[1])
            if rt not in obs:
                resources.append(rt)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Strategy: pick move that maximizes our advantage over opponent on best resource,
    # with fallback to corner opposite opponent.
    target_default = (w - 1 - ox, h - 1 - oy)

    best = None
    for dx, dy, nx, ny in moves:
        if resources:
            score = -10**9
            for rx, ry in resources:
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                # prefer taking resources we can get first; penalize letting opponent take.
                s = (opd - myd) * 10 - myd
                if (opd == myd):
                    s += 2
                score = s if s > score else score
            # small tie-break toward center to reduce oscillation
            s2 = score - 0.01 * (abs(nx - (w-1)/2) + abs(ny - (h-1)/2))
        else:
            s2 = -man(nx, ny, target_default[0], target_default[1])
        cand = (s2, -man(nx, ny, ox, oy), dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[2], best[3]]