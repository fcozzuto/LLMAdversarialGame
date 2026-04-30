def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # Choose a deterministic target: maximize (opp distance - my distance), tie by my distance.
    tx, ty = ((w - 1) // 2, (h - 1) // 2)
    if resources:
        best = None
        for rx, ry in resources:
            myd = abs(sx - rx) + abs(sy - ry)
            opd = abs(ox - rx) + abs(oy - ry)
            key = (-(opd - myd), myd, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        myd = abs(nx - tx) + abs(ny - ty)
        # Prefer getting closer to target
        s = myd * 3
        # If opponent is close to the same target, avoid them a bit
        opd_next = abs(ox - tx) + abs(oy - ty)
        s += (0 if opd_next >= 999999 else 0)
        # Add spacing from opponent position
        s -= min(8, abs(nx - ox) + abs(ny - oy))
        # Small preference to move toward target without getting stuck near obstacles
        adj_obs = 0
        for a in (-1, 0, 1):
            for b in (-1, 0, 1):
                if a == 0 and b == 0:
                    continue
                if (nx + a, ny + b) in obstacles:
                    adj_obs += 1
        s += adj_obs * 2
        return s

    best_dx, best_dy, best_s = moves[0][0], moves[0][1], None
    for dx, dy in moves:
        s = score_move(dx, dy)
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < (best_dx, best_dy)):
            best_s = s
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]