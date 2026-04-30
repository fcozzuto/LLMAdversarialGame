def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Candidate moves in deterministic order (prefer staying last-ish)
    moves = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))
    moves.append((0, 0))

    def man(a, b):  # manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource where we have positional advantage over the opponent
    best_r = None
    best_v = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        dS = abs(sx - rx) + abs(sy - ry)
        dO = abs(ox - rx) + abs(oy - ry)
        v = (dO - dS) * 10
        if dS == 0:
            v += 100000
        # Prefer resources closer to us when advantage ties
        v -= dS * 2
        # Slight preference for central-ish squares
        v -= (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.2
        if best_v is None or v > best_v:
            best_v = v
            best_r = (rx, ry)
        elif v == best_v:
            if (rx, ry) < best_r:
                best_r = (rx, ry)

    # If no resources, drift toward opponent (aggressive block)
    if best_r is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_r[0], best_r[1]

    cx, cy = sx, sy
    curr_dopp = abs(cx - ox) + abs(cy - oy)

    # Greedy step toward target with obstacle avoidance and opponent-aware pressure
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist_to_t = abs(nx - tx) + abs(ny - ty)
        dopp = abs(nx - ox) + abs(ny - oy)
        # If opponent is very close, avoid getting closer (unless capturing)
        opp_pen = 0
        if dopp <= 2:
            opp_pen = (2 - dopp + 1) * 8
            if dopp < curr_dopp:
                opp_pen += 6
        # Small bonus for moving onto target
        cap_bonus = 0
        if (nx, ny) == (tx, ty):
            cap_bonus = 120
        score = dist_to_t + opp_pen - cap_bonus
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]