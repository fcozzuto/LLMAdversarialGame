def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    r_self = (observation.get("self_role", "") or "").lower()
    r_opp = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in r_self) or ("pursuer" in r_self) or (r_opp == "")
    if not (("purs" in r_self) or ("pursuer" in r_self)) and ("purs" in r_opp):
        pursuer = True
    if not (("purs" in r_self) or ("pursuer" in r_self)) and ("pursuer" in r_opp):
        pursuer = True

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    start = (sx, sy)
    target = (ox, oy)

    def bfs_dist(st):
        if st == target:
            return 0
        lim = 10
        q = [st]
        dist = {st: 0}
        i = 0
        while i < len(q):
            x, y = q[i]
            i += 1
            d = dist[(x, y)]
            if d >= lim:
                continue
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obs:
                    continue
                if (nx, ny) in dist:
                    continue
                nd = d + 1
                if (nx, ny) == target:
                    return nd
                dist[(nx, ny)] = nd
                q.append((nx, ny))
        return 10**9

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dpath = bfs_dist((nx, ny))
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if pursuer:
            score = (dpath, d2)  # minimize
            better = best_score is None or score < best_score
        else:
            score = (-dpath, -d2)  # maximize
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]