def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("evader" in self_role)
    opp_evader = ("evad" in opp_role) or ("evader" in opp_role)
    # If roles are ambiguous, assume pursuit_direct means opponent pursues, so we evade.
    if ("purs" in self_role) or ("evad" in opp_role):
        self_evader = not ("purs" in self_role)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def neighbors(x, y):
        res = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                res.append((nx, ny))
        return res

    # BFS shortest path distance (8-neighborhood) with depth cap for speed
    def bfs_dist(start, goal, cap=6):
        if start == goal:
            return 0
        from_x, from_y = start
        gx, gy = goal
        seen = {(from_x, from_y)}
        frontier = [(from_x, from_y, 0)]
        best = None
        while frontier:
            x, y, d = frontier.pop(0)
            if d >= cap:
                continue
            nd = d + 1
            for nx, ny in neighbors(x, y):
                if (nx, ny) in seen:
                    continue
                if (nx, ny) == (gx, gy):
                    return nd
                seen.add((nx, ny))
                frontier.append((nx, ny, nd))
        return best if best is not None else (cap + 1)

    options = neighbors(sx, sy)
    if not options:
        return [0, 0]

    # Heuristic: evaluate candidate next position by BFS distance to opponent; add tie-breakers
    best = None
    best_key = None
    for nx, ny in options:
        dist = bfs_dist((nx, ny), (ox, oy), cap=6)
        man = abs(nx - ox) + abs(ny - oy)
        # Prefer escaping corridors: keep moves that increase mobility
        mob = len(neighbors(nx, ny))
        # If we are pursuer, we minimize distance and mobility opponent can use is irrelevant
        key = (-dist, -mob, -man) if self_evader else (dist, -mob, man)
        if best is None or key < best_key:
            best = (nx, ny)
            best_key = key

    dx = best[0] - sx
    dy = best[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]