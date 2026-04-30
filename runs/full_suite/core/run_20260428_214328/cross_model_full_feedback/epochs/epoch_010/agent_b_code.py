def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = [(p[0], p[1]) for p in (observation.get("resources", []) or [])]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # avoid invalid cells
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): continue
        if (nx, ny) in obstacles: continue
        if (nx, ny) == (ox, oy): continue
        candidates.append((dx, dy))

    if not candidates:
        return [0, 0]

    def manh(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    best_resource = None
    best_score = None
    for rx, ry in resources:
        if not inside(rx, ry) or (rx, ry) in obstacles: continue
        ds = manh((sx, sy), (rx, ry))
        do = manh((ox, oy), (rx, ry))
        # favor resources closer to us and far from opponent
        score = (do - ds)  # larger means we are closer to resource than opponent
        if best_score is None or score > best_score:
            best_score = score
            best_resource = (rx, ry)

    target = None
    if best_resource is not None:
        rx, ry = best_resource
        # require some advantage to pursue
        if best_score is not None and best_score >= 1:
            target = (rx, ry)

    if target is None and resources:
        # fall back to move toward nearest resource
        nearest = None; ndist = None
        for rx, ry in resources:
            if not inside(rx, ry) or (rx, ry) in obstacles: continue
            d = manh((sx, sy), (rx, ry))
            if ndist is None or d < ndist:
                ndist = d; nearest = (rx, ry)
        target = nearest if nearest is not None else None

    if target is not None:
        tx, ty = target
        dx = 1 if tx > sx else -1 if tx < sx else 0
        dy = 1 if ty > sy else -1 if ty < sy else 0
        # ensure move not into obstacle or opponent; if would, stay
        if (sx+dx, sy+dy) in obstacles or (sx+dx, sy+dy) == (ox, oy) or not inside(sx+dx, sy+dy):
            return [0, 0]
        return [dx, dy]

    # else, default: move toward opponent to contest, but avoid blocking
    dx = 1 if ox > sx else -1 if ox < sx else 0
    dy = 1 if oy > sy else -1 if oy < sy else 0
    if (sx+dx, sy+dy) in obstacles or (sx+dx, sy+dy) == (ox, oy) or not inside(sx+dx, sy+dy):
        return [0, 0]
    return [dx, dy]