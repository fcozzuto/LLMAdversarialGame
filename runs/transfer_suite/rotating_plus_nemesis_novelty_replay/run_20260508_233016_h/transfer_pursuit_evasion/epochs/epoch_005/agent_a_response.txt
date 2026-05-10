def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" in opp_role and "evad" not in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (int(observation.get("turn_index", 0)) & 1) == 1:
        deltas = list(reversed(deltas))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def nearest_obs_dist(x, y):
        if not obs:
            return 9
        md = 999
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    def minedge(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        nd = nearest_obs_dist(nx, ny)
        edge = minedge(nx, ny)

        if pursuer:
            # Minimize: approach opponent, avoid being adjacent to obstacles, drift to edges to constrain opponent.
            obs_pen = 0 if nd >= 2 else (2 - nd) * 2 + (1 if nd == 1 else 0)
            val = dist + 0.3 * obs_pen + 0.05 * edge
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            # Maximize: move away from pursuer, keep distance from obstacles, prefer staying away from corners.
            obs_avoid = 0 if nd >= 3 else (3 - nd) * 1.5
            val = dist + 0.4 * obs_avoid + 0.05 * edge
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]