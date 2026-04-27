def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        def dist(a, b):
            return abs(a[0]-b[0]) + abs(a[1]-b[1])
        best = None
        for rx, ry in resources:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            val = od - sd
            if best is None or val > best[0] or (val == best[0] and sd < best[1]):
                best = (val, sd, rx, ry)
        tx, ty = best[2], best[3]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def score_pos(px, py):
        # Prefer grabbing resources soon, and deny opponent access.
        if resources:
            bestv = None
            for rx, ry in resources:
                if (px, py) == (rx, ry):
                    v = 10**6
                else:
                    sd = abs(px-rx) + abs(py-ry)
                    od = abs(ox-rx) + abs(oy-ry)
                    v = od - sd
                if bestv is None or v > bestv:
                    bestv = v
            return bestv
        # No resources: drift toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return -((px-cx)*(px-cx) + (py-cy)*(py-cy))

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Small deterministic tie-break: closer to chosen target.
        s1 = score_pos(nx, ny)
        s2 = abs(nx - tx) + abs(ny - ty)
        key = (s1, -s2, -abs(ox - nx) - abs(oy - ny))
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]