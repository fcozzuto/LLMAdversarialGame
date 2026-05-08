def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def free_neighbors_count(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    def nearest_resource_dist2(x, y):
        res = observation.get("resources", []) or []
        best = 10**18
        for r in res:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                d2 = (x - rx) * (x - rx) + (y - ry) * (y - ry)
                if d2 < best:
                    best = d2
        return best if best != 10**18 else 0

    best_score = float("-inf")
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        fn = free_neighbors_count(nx, ny)
        rdist2 = nearest_resource_dist2(nx, ny)
        score = dist2 * 10 + fn - (rdist2 * 0.0005)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score:
            if [dx, dy] < best_move:
                best_move = [dx, dy]
    return best_move