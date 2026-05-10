def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles", [])
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or (("evad" in opp_role) and ("evad" not in self_role))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors(x, y):
        out = []
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                out.append((nx, ny))
        return out

    def bfs_dist(a, b, limit=14):
        if a == b:
            return 0
        ax, ay = a
        bx, by = b
        if not in_bounds(bx, by) or (bx, by) in obs_set:
            return limit + 1
        q = [(ax, ay, 0)]
        seen = {(ax, ay)}
        i = 0
        while i < len(q):
            x, y, d = q[i]
            i += 1
            if d >= limit:
                continue
            for nx, ny in neighbors(x, y):
                if (nx, ny) in seen:
                    continue
                nd = d + 1
                if (nx, ny) == (bx, by):
                    return nd
                seen.add((nx, ny))
                q.append((nx, ny, nd))
        return limit + 1

    if pursuer:
        target = (ox, oy)
    else:
        target = max(corners, key=lambda c: abs(c[0]-ox) + abs(c[1]-oy))

    best = (0, 0)
    best_val = None
    cx, cy = target

    # Deterministic move ordering: fixed deltas; tie-break by lexicographic dx,dy
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        d_opp = abs(nx - ox) + abs(ny - oy)
        d_corner = abs(nx - cx) + abs(ny - cy)
        neigh = len(neighbors(nx, ny))

        # obstacle-aware distance to opponent with limited BFS
        path_to_opp = bfs_dist((nx, ny), (ox, oy), 12)

        # Evader vs pursuer scoring
        if pursuer:
            # Prefer shortest path pursuit; discourage getting boxed near obstacles.
            val = -path_to_opp * 10.0 - d_opp * 2.0 + neigh * 0.2
        else:
            # Prefer farthest (path-wise) while still trending toward a far corner.
            val = path_to_opp * 10.0 + d_opp * 2.0 + d_corner * 0.8 + neigh * 0.15
            # Small penalty for moving to a cell that is too "crowded" (helps vs zigzag squeezes)
            val -= (8 - neigh) * 0.25

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]