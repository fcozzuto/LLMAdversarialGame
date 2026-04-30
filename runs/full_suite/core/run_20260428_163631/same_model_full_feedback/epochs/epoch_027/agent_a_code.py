def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = w - 1, h - 1
        if (sx + sy) > (ox + oy):
            tx, ty = 0, 0
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = man(nx, ny, tx, ty)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        # If we can grab a resource immediately, prioritize it strongly.
        v = 10**9
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Prefer resources where we're closer than opponent; tie-break by our closeness.
            cand = d_self - d_opp * 0.9 + d_self * 0.02
            if d_self == 0:
                cand -= 1000
            if cand < v:
                v = cand
        # Slightly discourage moving away from overall resource region.
        # Use average resource centroid as deterministic guidance.
        cx = sum(r[0] for r in resources) / len(resources)
        cy = sum(r[1] for r in resources) / len(resources)
        v += 0.001 * man(nx, ny, int(cx), int(cy))
        if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]