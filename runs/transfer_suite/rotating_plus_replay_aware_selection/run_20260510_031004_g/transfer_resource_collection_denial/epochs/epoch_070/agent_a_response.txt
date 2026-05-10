def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # King-move distances (diagonals allowed, uniform step cost)
    best_key = None
    best_t = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)

        # Main objective: win the race; add tie-breaks favoring closeness and "higher" coords.
        # If opponent is closer, penalize heavily; if I can be strictly earlier, strongly reward.
        race_gap = opp_d - my_d
        key = (race_gap * 3000) - my_d * 3 + (my_d == 0) * 100000 + (-rx) * 0 + (-ry) * 0
        # Deterministic tie-break: prefer smaller my_d, then larger y, then larger x
        tie = (-my_d, -ry, -rx)
        full = (key, tie)
        if best_key is None or full > best_key:
            best_key = full
            best_t = (rx, ry)

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the direct target step would move onto an obstacle (rare), try alternate deterministic move.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
        best_alt = None
        for mdx, mdy in moves:
            ax, ay = sx + mdx, sy + mdy
            if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                continue
            my_d = cheb(ax, ay, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            race_gap = opp_d - my_d
            full = (race_gap * 3000) - my_d * 3, (-my_d, -ay, -ax)
            if best_alt is None or full > best_alt[0]:
                best_alt = (full, [mdx, mdy])
        return best_alt[1] if best_alt else [0, 0]

    return [dx, dy]