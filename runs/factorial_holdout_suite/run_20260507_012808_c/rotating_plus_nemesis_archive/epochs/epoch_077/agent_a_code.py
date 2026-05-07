def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def mdist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Evaluate each candidate move by the best resource we can "beat" the opponent to.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_pos = (nx, ny)
        cur_best = -10**18
        for rx, ry in resources:
            r = (rx, ry)
            my_d = mdist(my_pos, r)
            opp_d = mdist((ox, oy), r)
            # Primary: maximize lead advantage (opp_d - my_d).
            lead = opp_d - my_d
            # Secondary: prefer closer targets once lead is comparable; also slight preference to resources nearer the center.
            center_bias = -0.01 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            val = 1000 * lead - 2 * my_d + center_bias
            if val > cur_best:
                cur_best = val
        # Deterministic tie-break: prefer lexicographically smaller move among equal values.
        if cur_best > best_val or (cur_best == best_val and (dx, dy) < best_move):
            best_val = cur_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]