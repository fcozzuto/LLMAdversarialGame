def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # deterministic retreat towards the farthest corner from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = None
        for cx, cy in corners:
            v = man(ox, oy, cx, cy) - man(sx, sy, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (cx, cy) < best):
                bestv = v
                best = (cx, cy)
        tx, ty = best
    else:
        # Prefer resources where we are much closer than opponent; otherwise, block by racing a different reachable one.
        best = None
        bestv = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # If opponent is currently closer, heavily penalize; else reward strong leads.
            lead = do - ds
            # Secondary term: prefer closer-to-us targets (faster capture).
            v = lead * 100 - ds
            if bestv is None or v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    cand = []
    if dx != 0 or dy != 0:
        cand.append((dx, dy))
        cand.append((dx, 0))
        cand.append((0, dy))
        cand.append((0, 0))
    else:
        cand.append((0, 0))

    # If blocked, pick the first candidate that is in-bounds and not into an obstacle.
    for mdx, mdy in cand:
        nx, ny = sx + mdx, sy + mdy
        if inb(nx, ny):
            return [int(mdx), int(mdy)]
    return [0, 0]