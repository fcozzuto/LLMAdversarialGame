def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obst_risk(x, y):
        if (x, y) in occ:
            return 10**9
        risk = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            if (x+dx, y+dy) in occ:
                risk += 40
        for dx, dy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            if (x+dx, y+dy) in occ:
                risk += 15
        return risk

    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_delta = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in occ:
            continue

        my_step_risk = obst_risk(nx, ny)
        if my_step_risk >= 10**8:
            continue

        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            d_my = manh(nx, ny, rx, ry)
            d_op = manh(ox, oy, rx, ry)

            # Avoid "free" pickups for the opponent and heavily obstacle-adjacent goals
            danger = 0
            if manh(rx, ry, ox, oy) <= 1:
                danger += 400
            danger += obst_risk(rx, ry) // 2

            # Prefer resources we can reach much sooner than opponent
            val = (d_op - d_my) * 45 - d_my * 2 - danger
            if val > local_best:
                local_best = val

        # If multiple moves similar, keep deterministic by preferring smaller deltas
        if local_best > best_val or (local_best == best_val and (dx, dy) < best_delta):
            best_val = local_best
            best_delta = (dx, dy)

    return [best_delta[0], best_delta[1]]