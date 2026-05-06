def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Avoid being on same row as opponent when close (opponent sweep rows)
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            row_pen = 3 if ny == oy and d <= 3 else 0
            v = d - row_pen
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Defensive bias against row-sweep interception
        opp_close = md(nx, ny, ox, oy) <= 3
        row_same = (ny == oy)
        defend = 2 if (opp_close and row_same) else 0

        # Choose move that maximizes advantage on the best future resource
        local_best = -10**18
        for tx, ty in resources:
            self_d = md(nx, ny, tx, ty)
            opp_d = md(ox, oy, tx, ty)
            # Prefer resources where we are closer than opponent, then faster completion
            adv = opp_d - self_d
            val = adv * 10 - self_d
            if val > local_best:
                local_best = val

        total = local_best - defend
        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move