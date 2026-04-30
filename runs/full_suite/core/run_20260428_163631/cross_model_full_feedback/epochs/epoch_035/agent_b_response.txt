def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst: resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def manh(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    best_move = None
    best_score = -10**9

    # Simple deterministic heuristic:
    # 1) If a resource is reachable now (in one step), move toward it.
    # 2) Else move to maximize distance from opponent while staying close to center to collect more later.
    if resources:
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            for rx, ry in resources:
                if abs(nx - rx) + abs(ny - ry) == 0:
                    return [dx, dy]
        # else pick move that reduces distance to nearest resource
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            nd = min(manh((nx, ny), r) for r in resources)
            if best_score is None or nd < best_score:
                best_score = nd
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # No immediate resource gain; move to maximize distance from opponent but not step off grid
    center_x, center_y = w // 2, h // 2
    best = None
    best_score = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_center = abs(nx - center_x) + abs(ny - center_y)
        score = dist_opp * -1 + dist_center * 0  # prioritize distancing slightly
        if score > best_score:
            best_score = score
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]

    # Fallback
    return [0, 0]