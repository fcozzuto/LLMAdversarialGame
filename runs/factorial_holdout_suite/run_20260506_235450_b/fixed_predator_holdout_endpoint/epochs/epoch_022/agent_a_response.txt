def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    if not resources:
        return [0, 0]

    turn = int(observation.get("turn_index", 0) or 0)

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    # Neighbor order deterministic; slightly rotated each turn
    base = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    r0 = turn % 9
    moves = base[r0:] + base[:r0]

    # Choose best target resource we can contest; otherwise pick best anyway
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive => we are closer
        # Prefer: contestable (adv>0), then closer, then stable hash
        hsh = ((rx * 53 + ry * 97) ^ (sd * 11 + od * 7)) & 2047
        key = (1 if adv > 0 else 0, adv, -sd, -od, hsh)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    # If opponent is closer to all resources, go for the single nearest (still deterministic)
    # (Handled by best_r selection key.)

    # Evaluate candidate one-step moves with obstacle avoidance and opponent pressure
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_to_t = md(nx, ny, tx, ty)
        opp_to_t = md(ox, oy, tx, ty)
        # Encourage reducing distance to target; also avoid moves that give opponent much advantage
        adv_after = opp_to_t - my_to_t

        # Local resource pressure: prefer moves that get closer to any resource where we are advantaged
        local = 0
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Weighted advantage proxy; cap to keep scale small
            local += max(0, (od - d)) + (1 if (rx, ry) == (tx, ty) else 0)
        # Tie-break by prefer staying only if equally good
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        # Stable hash for tie-break
        hsh2 = ((nx * 31 + ny * 37) ^ (my_to_t * 13 + opp_to_t * 17)) & 1023
        key = (adv_after, -my_to_t, local, -stay_pen, hsh2)

        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    # If all moves illegal (extreme), stay
    return [int(best_move[0]), int(best_move[1])]