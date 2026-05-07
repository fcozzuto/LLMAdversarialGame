def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestv = -10**18
        bestm = (0, 0)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            v = -d
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    # Directly grab if reachable next step
    for tx, ty in resources:
        if abs(tx - sx) <= 1 and abs(ty - sy) <= 1:
            dx = 0 if tx == sx else (1 if tx > sx else -1)
            dy = 0 if ty == sy else (1 if ty > sy else -1)
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]

    # Otherwise, compete for the most "swingable" resource; prioritize those on opponent sweep-aligned lines.
    best_target = None
    best_score = -10**18
    for tx, ty in resources:
        my_d = abs(tx - sx) + abs(ty - sy)
        if opp_exists:
            opp_d = abs(tx - ox) + abs(ty - oy)
            deny = opp_d - my_d
        else:
            deny = 0
        sweep_bonus = 0
        if opp_exists:
            if tx == ox or ty == oy:
                sweep_bonus = 2  # sweep_rows-style alignment heuristic
        # Encourage closeness when denying is weak
        score = deny * 3 + sweep_bonus - my_d * 0.2
        if score > best_score:
            best_score = score
            best_target = (tx, ty)

    tx, ty = best_target
    # Greedy step toward target with obstacle-aware tie-breaking; also keep deny pressure.
    bestv = -10**18
    bestm = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_nd = abs(tx - nx) + abs(ty - ny)
        if opp_exists:
            # Predict opponent pressure by how close they'd be to the same target
            opp_d = abs(tx - ox) + abs(ty - oy)
            v = (opp_d - my_nd) * 2 - my_nd * 0.5
        else:
            v = -my_nd
        # small deterministic bias to break ties: prefer moving closer in x then y
        v += -(0.01 * (abs(nx - tx) - abs(sx - tx) + abs(ny - ty) - abs(sy - ty)))
        if v > bestv:
            bestv, bestm = v, (dx, dy)

    return [bestm[0], bestm[1]]