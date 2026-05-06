def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def dist(a, b, c, d): return abs(c - a) + abs(d - b)

    def best_target(px, py):
        dpo = dist(px, py, ox, oy)
        best = None
        bestk = -10**9
        for rx, ry in resources:
            myd = dist(px, py, rx, ry)
            opd = dist(ox, oy, rx, ry)
            base = (opd - myd)
            # If opponent is very near, prefer slightly farther-but-safer targets to avoid direct denial.
            if dpo <= 2:
                base = (opd - myd) - 0.35 * myd
            # Encourage taking closer when not heavily contested
            if opd > myd:
                base += 0.25 * (opd - myd)
            # Tie-break deterministically by coordinates
            key = base + (rx * 0.001 + ry * 0.000001)
            if key > bestk:
                bestk = key
                best = (rx, ry)
        return best

    tx, ty = best_target(sx, sy)

    # Predict opponent next greedy step toward its best target
    otx, oty = best_target(ox, oy)
    pred_ox, pred_oy = ox, oy
    best_op = -10**9
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer moves that reduce distance to its target
        nd = dist(nx, ny, otx, oty)
        score = -nd + (nx - ox) * 0.0001 + (ny - oy) * 0.000001
        if score > best_op:
            best_op = score
            pred_ox, pred_oy = nx, ny

    # Choose our move: maximize contested resource gain while keeping pressure on predicted opponent step
    best = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = dist(nx, ny, tx, ty)
        # Resource value: prefer being closer than opponent to the chosen target
        oppd = dist(pred_ox, pred_oy, tx, ty)
        res_score = (oppd - myd)
        # Denial pressure: reduce distance to where opponent will likely be
        pressure = -dist(nx, ny, pred_ox, pred_oy)
        # Small bias to avoid drifting when already on target
        on_bias = 0.2 if (nx, ny) == (tx, ty) else 0.0
        val = 1.0 * res_score + 0.45 * pressure + on_bias
        # Deterministic tie-break
        val += (dx * 0.0001 + dy * 0.00001)
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best