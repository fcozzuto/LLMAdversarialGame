def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            myd = man(sx, sy, cx, cy)
            od = man(ox, oy, cx, cy)
            val = myd - 0.25 * od
            if best is None or val < best[0]:
                best = (val, cx, cy)
        if best is None:
            return [0, 0]
        tx, ty = best[1], best[2]
    else:
        best = None
        for rx, ry in resources:
            myd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            val = myd - 0.65 * od
            if best is None or val < best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    bestm = None
    for dx, dy, nx, ny in moves:
        myd = man(nx, ny, tx, ty)
        od = man(nx, ny, ox, oy)
        tv = myd - 0.05 * od
        # small tie-break: prefer moves that reduce our distance to target
        if bestm is None or tv < bestm[0]:
            bestm = (tv, dx, dy)
    return [int(bestm[1]), int(bestm[2])]