def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obs_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    c += 1
        return c

    # Strategy shift: avoid "od-sd only". Instead, pick resources we can win soon (sd < od),
    # otherwise choose a denial target near where opponent is headed.
    def best_target_for_pos(x, y, oppx, oppy):
        best = None
        for rx, ry in resources:
            sd = manh((x, y), (rx, ry))
            od = manh((oppx, oppy), (rx, ry))
            win_soon = 1 if sd < od else 0
            # Prefer immediate win, then closer-for-us, and discourage easy access for opponent.
            key = (win_soon, (od - sd), -sd, -od, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    # One-step lookahead: evaluate each move by the best target we could aim for next.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    best_move = (0, 0)
    best_val = None

    target_fallback = best_target_for_pos(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            val = -1e9
        else:
            tx, ty = best_target_for_pos(nx, ny, ox, oy)
            sd = manh((nx, ny), (tx, ty))
            od = manh((ox, oy), (tx, ty))
            # If we land on a resource, dominate.
            pick_bonus = 1000 if (nx, ny) == (tx, ty) else 0
            # Encourage moving toward a currently winnable target; if not winnable, reduce opponent's advantage.
            win_bonus = 200 if sd < od else 0
            block_pen = 12 * obs_adj(nx, ny)
            # Additional small tie-break: avoid letting opponent get much closer than us.
            opp_adv_pen = 5 * max(0, sd - od)
            # Slight preference to not run directly into obstacles-adjacent regions.
            val = pick_bonus + win_bonus + (od - sd) * 10 - block_pen - opp_adv_pen
            # If no clear win target changed, keep a stable drift toward a fallback target.
            if (tx, ty) == target_fallback:
                val += 1
        key2 = (val, -abs(dx), -abs(dy), dx, dy)
        if best_val is None or key2 > best_val:
            best_val = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]