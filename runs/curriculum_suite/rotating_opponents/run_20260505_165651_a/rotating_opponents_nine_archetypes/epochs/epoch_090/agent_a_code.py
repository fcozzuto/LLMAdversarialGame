def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def neighbors(x, y):
        m = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
        out = []
        for dx, dy in m:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                out.append((dx, dy))
        return out

    # Competitive target: prioritize resources we can reach before opponent (opp_d - self_d),
    # with a fallback preference for resources far from opponent.
    best_r = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # "Go-for-win": large when we are closer; "Deny": also prefer attacking opponent-favored spots.
        val = (od - sd) * 100 - sd - (0 if od >= sd else (sd - od)) * 10 + (w + h - (rx + ry)) * 0
        # Deterministic tie-break by coordinates
        if val > best_val or (val == best_val and (rx, ry) < best_r):
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r

    moves = neighbors(sx, sy)
    # If somehow no moves possible, stay.
    if not moves:
        return [0, 0]

    # Greedy step that improves competitive value; tie-break toward aligning axes then diagonals.
    best_move = moves[0]
    best_mval = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        mval = (od - sd) * 100 - sd
        # Tie-break: prefer smaller remaining distance, then deterministic direction ordering bias
        rem = sd
        dir_bias = (0 if (dx == 0 or dy == 0) else 1, abs(dx) + abs(dy), dx, dy)
        key = (mval, -rem, -dir_bias[0], -dir_bias[1], dir_bias[2], dir_bias[3])
        bkey = (best_mval, -man(sx + best_move[0], sy + best_move[1], tx, ty), -0, 0, 0, 0)
        if mval > best_mval or (mval == best_mval and rem < man(sx + best_move[0], sy + best_move[1], tx, ty)):
            best_mval = mval
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]