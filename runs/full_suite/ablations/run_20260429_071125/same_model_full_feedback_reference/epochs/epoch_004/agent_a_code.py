def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles_in = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles_in:
        if p is not None and len(p) >= 2:
            x, y = p[0], p[1]
            if x is not None and y is not None:
                obs.add((int(x), int(y)))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = p[0], p[1]
            if x is not None and y is not None:
                tx, ty = int(x), int(y)
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                    res.append((tx, ty))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not inb(sx, sy) or w <= 0 or h <= 0:
        return [0, 0]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    # Prefer stepping onto a resource if possible; else go to nearest resource; else approach opponent.
    target = None
    if res:
        bestd = 10**9
        for rx, ry in res:
            d = abs(rx - sx) + abs(ry - sy)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    best = (0, 0, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if target is not None:
            base = -(abs(target[0] - nx) + abs(target[1] - ny))
        else:
            base = -(abs(ox - nx) + abs(oy - ny))

        # Small penalty for being adjacent to obstacles to reduce getting stuck.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if inb(x2, y2) and (x2, y2) in obs:
                    adj += 1

        # Big bonus if landing on a resource.
        res_bonus = 0
        if target is not None and (nx, ny) == target:
            res_bonus = 10**6

        score = base * 100 - adj + res_bonus
        if score > best[2]:
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]