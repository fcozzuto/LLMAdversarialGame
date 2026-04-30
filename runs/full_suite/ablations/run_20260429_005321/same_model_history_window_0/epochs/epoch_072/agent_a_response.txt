def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        # drift toward opponent corner deterministically
        tx, ty = ox, oy
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d2 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                cand = (d2, dx, dy)
                if best is None or cand < best:
                    best = cand
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx*dx + dy*dy

    best_score = None
    best_target = resources[0]
    for r in resources:
        sd = dist2((sx, sy), r)
        od = dist2((ox, oy), r)
        # prefer resources we can reach sooner; if tied, prefer farther from opponent
        score = (od - sd, -sd, r[0], r[1])
        if best_score is None or score > best_score:
            best_score = score
            best_target = r

    tx, ty = best_target
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d2n = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        # deterministic tie-break: prefer reducing distance; then closer to opponent (block a bit); then delta order
        d2o = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        cand = (d2n, d2o, dx, dy)
        if best is None or cand < best:
            best = cand
    if best is None:
        return [0, 0]
    return [best[2], best[3]]