def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy  # Chebyshev distance

    res_set = set(tuple(r) for r in resources)
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    def best_target_score(px, py):
        # Prefer resources where we are closer than opponent (dO - dS large), then smaller dS.
        best = (-10**9, 10**9)
        for rx, ry in resources:
            dS = cd(px, py, rx, ry)
            dO = cd(ox, oy, rx, ry)
            sc = dO - dS
            cand = (sc, dS)
            if cand > best:
                best = cand
        return best

    best_move = [0, 0]
    best_val = (-10**18, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        collected_now = 1 if (nx, ny) in res_set else 0
        sc, dS = best_target_score(nx, ny)
        # Strongly prioritize stepping onto a resource; otherwise maximize relative advantage and reduce own distance.
        val = (collected_now, sc, -dS)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move