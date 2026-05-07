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

    # If no resources, drift to safer corner far from opponent
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = man(sx, sy, cx, cy) - 0.05 * man(ox, oy, cx, cy)
            if best is None or d < best[0]:
                best = (d, cx, cy)
        if best is None:
            return [0, 0]
        _, tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Choose resource with best self advantage and proximity
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources closer to us than opponent; tie-break by fewer steps and lower opponent distance
        score = (do - ds, -ds, do, rx + ry * 0.001)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    # Greedy local move among valid adjacent squares toward target, with obstacle avoidance
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, tx, ty)
        # Discourage stepping into positions that give opponent an advantage to same target
        no = man(ox, oy, tx, ty)
        # Include a small bias to reduce our distance and maintain parity-like regularity deterministically
        bias = 0.001 * ((nx * 7 + ny * 13) % 10)
        val = (-ns, -(ns - (no - ns)) if True else 0, bias)
        if bestm is None or val > bestm[0]:
            bestm = (val, dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]