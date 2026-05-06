def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def mdist(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    # Prefer resources we can reach first; also slightly prefer resources that break opponent row sweeping.
    opp_row_pressure = 0
    if oy == sy:
        opp_row_pressure = 3  # stronger when on same row
    best = None
    best_key = None
    for rx, ry in resources:
        sd = mdist(rx, ry, sx, sy)
        od = mdist(rx, ry, ox, oy)
        # Base advantage: positive if we are closer than opponent
        val = (od - sd) * 10 - sd
        # Avoid feeding opponent: if opponent is already closer, heavily discount
        if od <= sd:
            val -= 60 + (sd - od) * 10
        # Break sweep: if opponent shares our row, prefer changing row (targets with different y)
        if opp_row_pressure and ry == oy:
            val -= 25 * opp_row_pressure
        # Tie-break deterministically by (higher val, smaller sd, lex)
        key = (val, -sd, -rx, -ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (0, 0), (-dx, dy), (-dx, 0), (0, -dy), (-dx, -dy)]
    # Evaluate candidate moves by resulting distance to target (and discourage stepping into obstacles).
    bestm = [0, 0]
    bestv = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        v = mdist(nx, ny, tx, ty)
        if (ox == ny) and (oy != ny):
            v += 2
        # Deterministic tie-break
        key = (v, mx, my)
        if bestv is None or key < bestv:
            bestv = key
            bestm = [mx, my]

    return bestm