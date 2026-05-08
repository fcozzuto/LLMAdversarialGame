def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    cand = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist_to_resources(x, y):
        if not resources:
            return 0
        m = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < m:
                m = d
        return m

    best = None
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dT = mindist_to_resources(nx, ny)
        dO = abs(ox - nx) + abs(oy - ny)
        v = (-dT) * 1000 + dO
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]