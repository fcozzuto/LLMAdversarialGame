def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs_set.add((int(p[0]), int(p[1])))

    r_self = (observation.get("self_role", "") or "").lower()
    r_opp = (observation.get("opponent_role", "") or "").lower()

    is_pursuer = ("purs" in r_self) or ("pursuer" in r_self) or ("pursuit" in r_self)
    is_evader = ("evad" in r_self) or ("runner" in r_self)
    if not is_pursuer and not is_evader:
        is_pursuer = ("purs" in r_opp) or ("pursuer" in r_opp)
        is_evader = not is_pursuer

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs_dist(start, goal, limit=8):
        if start == goal:
            return 0
        q = [start]
        dist = {start: 0}
        i = 0
        while i < len(q):
            x, y = q[i]
            i += 1
            d = dist[(x, y)]
            if d >= limit:
                continue
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                    continue
                if (nx, ny) in dist:
                    continue
                nd = d + 1
                if (nx, ny) == goal:
                    return nd
                dist[(nx, ny)] = nd
                q.append((nx, ny))
        return None

    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    best_move = [0, 0]
    if is_pursuer:
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            d = bfs_dist((nx, ny), (ox, oy), 8)
            if d is None:
                val = -cheb((nx, ny), (ox, oy))
            else:
                val = -d
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        best_val = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            d = bfs_dist((nx, ny), (ox, oy), 8)
            if d is None:
                val = cheb((nx, ny), (ox, oy))
            else:
                val = d
            # slight preference for moving away in direct line
            val += 0.01 * (abs(nx - ox) + abs(ny - oy))
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]