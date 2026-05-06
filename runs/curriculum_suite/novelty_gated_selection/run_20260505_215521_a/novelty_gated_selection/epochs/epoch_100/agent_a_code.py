def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy, nx, ny in valid:
            d = manh(nx, ny, tx, ty)
            # slight preference to avoid opponent if tie
            d2 = d * 10 + manh(nx, ny, ox, oy)
            if d2 < best[0]:
                best = (d2, dx, dy)
        return [best[1], best[2]]

    alpha = 0.7
    # For each move, choose the resource that best combines closeness and denying (being closer than opponent)
    best_val = 10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in valid:
        val = 10**18
        for rx, ry in resources:
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            # minimize: 1.7*ds - 0.7*do  (equivalently ds - alpha*(do-ds))
            v = (1.7 * ds) - (0.7 * do)
            # tie-break: prefer closer to opponent when denying is equal
            if v < val:
                val = v
        # additional tie-break: avoid getting too close to obstacles is already ensured;
        # slight preference to keep distance from opponent when not denying
        val += 0.02 * manh(nx, ny, ox, oy)
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]