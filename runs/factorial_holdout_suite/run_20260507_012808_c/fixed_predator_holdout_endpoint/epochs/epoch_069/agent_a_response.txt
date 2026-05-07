def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cd(a, b):  # diagonal-allowed distance (Chebyshev)
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Candidate move deltas
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Find best resource by immediate advantage (opponent farther than us)
    best_r = None
    best_adv = None
    for rx, ry in resources:
        sd = cd((sx, sy), (rx, ry))
        od = cd((ox, oy), (rx, ry))
        adv = od - sd
        key = (adv, -sd, -od, -rx, -ry)  # maximize advantage, then closer
        if best_adv is None or key > best_adv:
            best_adv = key
            best_r = (rx, ry)

    tx, ty = best_r

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Move evaluation: (1) reduce distance to our target; (2) increase opp lead margin;
        # (3) prevent stepping into a closer position for opponent on that target.
        cur_sd = cd((sx, sy), (tx, ty))
        nxt_sd = cd((nx, ny), (tx, ty))
        cur_od = cd((ox, oy), (tx, ty))
        nxt_od = cd((ox, oy), (tx, ty))  # opponent position unchanged this turn

        opp_margin = (nxt_od - nxt_sd)  # how much we lead on target
        key = (opp_margin, -(nxt_sd), -(abs(nx - tx) + abs(ny - ty)), -abs(nx - ox) - abs(ny - oy), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    # If all filtered out (shouldn't happen), stay
    return best_move if best_move is not None else [0, 0]