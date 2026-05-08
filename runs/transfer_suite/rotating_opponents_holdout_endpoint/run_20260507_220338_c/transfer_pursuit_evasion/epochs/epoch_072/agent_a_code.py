def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("avoid" in role_s) or ("escape" in role_s) or ("escape" in str(observation.get("environment_name", "")).lower())
    is_pursuer = ("pursuer" in role_s) or ("chaser" in role_s) or ("hunter" in role_s) or ("catch" in role_s) or ("pursuit" in role_s)

    pursue = True if is_pursuer else (False if is_evader else True)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)

    best_val = None
    best_moves = []

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        d_cheb = max(abs(nx - ox), abs(ny - oy))
        d_man = abs(nx - ox) + abs(ny - oy)

        # Objective
        if pursue:
            val = -d_cheb * 10 - d_man
        else:
            val = d_cheb * 10 + d_man

        # Obstacle proximity penalty/bonus (deterministic local)
        near = 0
        for (bx, by) in blocked:
            if abs(bx - nx) <= 1 and abs(by - ny) <= 1:
                near += 1
        if pursue:
            val -= near * 2
        else:
            val -= near * 3

        # Tie-breaker: prefer a deterministic "direction" by turn parity
        # (helps avoid stalling/loops in symmetric situations)
        bias = 0
        if (t % 2) == 0:
            bias = (1 if (dx > 0 or (dx == 0 and dy > 0)) else 0) - (1 if (dx < 0 or (dx == 0 and dy < 0)) else 0)
        else:
            bias = (1 if (dx < 0 or (dx == 0 and dy > 0)) else 0) - (1 if (dx > 0 or (dx == 0 and dy < 0)) else 0)
        val += bias * 0.01

        if best_val is None or val > best_val:
            best_val = val
            best_moves = [(dx, dy)]
        elif val == best_val:
            best_moves.append((dx, dy))

    # Deterministic selection among best ties
    idx = (t + sx * 31 + sy * 17 + ox * 7 + oy * 13) % len(best_moves)
    dx, dy = best_moves[idx]
    return [int(dx), int(dy)]