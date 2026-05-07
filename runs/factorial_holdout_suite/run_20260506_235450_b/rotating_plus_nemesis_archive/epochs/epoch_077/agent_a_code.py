def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev (diagonal-friendly)

    # If no resources, just stay (deterministic)
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    opp_row = oy
    opp_col = ox

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        landed = (nx, ny) in set(resources)
        self_pos = (nx, ny)

        # Prefer moves that (1) allow immediate pickup, then (2) create the biggest advantage
        # against the opponent on the same resource targets, with slight row-interception bias.
        val = 0
        if landed:
            val += 10000

        row_bias = 0
        col_bias = 0
        if ny == opp_row:
            row_bias = 3
        if nx == opp_col:
            col_bias = 3

        # Evaluate best target under this move
        local_best = -10**18
        for rx, ry in resources:
            r = (rx, ry)
            sd = dist(self_pos, r)
            od = dist((ox, oy), r)
            # Advantage: we want larger (od - sd). Tie-break by shorter sd.
            adv = od - sd
            target_bonus = 0
            # Intercept heuristic: prefer targets aligned with opponent sweep axis
            if ry == opp_row:
                target_bonus += 1
            if rx == opp_col:
                target_bonus += 1
            score = adv * 10 - sd + target_bonus
            if score > local_best:
                local_best = score

        val += local_best + row_bias + col_bias

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]