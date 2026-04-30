def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_resource_from(x, y):
        # Closest by chebyshev (handles diagonals fairly)
        br, bd = resources[0], 10**9
        for r in resources:
            d = max(abs(r[0] - x), abs(r[1] - y))
            if d < bd or (d == bd and (r[0], r[1]) < br):
                bd, br = d, r
        return br

    target = best_resource_from(sx, sy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    tx, ty = target
    # Prefer moving that reduces distance to target; also avoid giving opponent an immediate advantage
    # by adding a mild penalty when getting closer to opponent only.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_t = max(abs(tx - nx), abs(ty - ny))
        dist_t0 = max(abs(tx - sx), abs(ty - sy))
        # opponent pressure: prefer moves that reduce our target distance more than theirs (deterministic)
        opp_dist = max(abs(tx - ox), abs(ty - oy))
        opp_gain = opp_dist - max(abs(tx - ox), abs(ty - oy))
        opp_close = max(abs(ox - nx), abs(oy - ny))
        score = 1000 * (dist_t0 - dist_t) - 2 * dist_t - 0.01 * opp_close + 0.5 * (opp_gain)
        candidates.append((score, -abs(nx - ox) - abs(ny - oy), (nx, ny)))
    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda z: (z[0], z[1], z[2][0], z[2][1]), reverse=True)
    nx, ny = candidates[0][2]
    return [nx - sx, ny - sy]