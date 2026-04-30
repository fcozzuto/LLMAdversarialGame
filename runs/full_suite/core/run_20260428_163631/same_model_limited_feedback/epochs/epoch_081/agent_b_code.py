def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    raw_resources = observation.get("resources", []) or []
    resources = []
    for r in raw_resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    obstacles = set()
    raw_obs = observation.get("obstacles", []) or []
    for p in raw_obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    opp = (ox, oy)
    cand = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cand.append((dx, dy, (nx, ny)))
    if not cand:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy, pos in cand:
        if resources:
            my_best = 10**18
            opp_best = 10**18
            for r in resources:
                d_my = dist2(pos, r)
                if d_my < my_best:
                    my_best = d_my
                d_opp = dist2(opp, r)
                if d_opp < opp_best:
                    opp_best = d_opp
            # Prefer being closer to resources than opponent; also prefer staying away from opponent a bit
            val = (opp_best - my_best) * 1000 - dist2(pos, opp)
        else:
            # No resources: move away from opponent
            val = dist2(pos, opp)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]