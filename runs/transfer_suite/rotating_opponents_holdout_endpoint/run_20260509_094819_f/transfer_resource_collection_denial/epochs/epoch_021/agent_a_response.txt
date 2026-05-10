def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    ds8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_value(px, py):
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry):
                continue
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources where we have a distance advantage; tie-break to closer ones.
            val = (od - sd, -sd)
            if best is None or val > best[0]:
                best = (val, rx, ry, sd, od)
        return best

    if not resources:
        return [0, 0]

    cur_best = best_value(sx, sy)
    if cur_best is None:
        return [0, 0]
    _, tx, ty, _, _ = cur_best

    # One-step lookahead: choose move maximizing the same objective for next position.
    best_move = (None, -10**9)
    for dx, dy in ds8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nb = best_value(nx, ny)
        if nb is None:
            continue
        (v1, v2), _, _, _, _ = nb
        # Strongly keep toward the selected target if it remains best.
        toward = -man(nx, ny, tx, ty)
        score = v1 * 1000 + v2 + toward
        if score > best_move[1]:
            best_move = ((dx, dy), score)

    if best_move[0] is None:
        # Fallback: simple greedy toward current target.
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy):
            return [dx, dy]
        for adx, ady in ds8:
            nx, ny = sx + adx, sy + ady
            if inb(nx, ny):
                return [adx, ady]
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]