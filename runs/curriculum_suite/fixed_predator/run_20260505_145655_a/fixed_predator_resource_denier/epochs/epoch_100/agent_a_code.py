def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deny: prioritize resources closest to opponent that we can reach near parity.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        reach = sd - od  # <=0 means we can deny earlier/equal
        # Prefer contested (low od), then prioritize reach closeness, then proximity to reduce path length.
        if reach <= 2:
            val = (-od) * 50 - max(reach, -3) * 10 - (sd * 0.1) - (rx + ry) * 0.001
            if best is None or val > best[0]:
                best = (val, rx, ry)
    if best is None:
        # Fallback: opportunistic as last resort
        best = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            val = (od - sd) * 30 - sd - (rx * 0.001 + ry * 0.001)
            if best is None or val > best[0]:
                best = (val, rx, ry)
    _, tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Choose move that reduces our distance to target and (slightly) keeps away from opponent.
    bestm = None
    for dx, dy, nx, ny in moves:
        d_t = man(nx, ny, tx, ty)
        d_o = man(nx, ny, ox, oy)
        cur_d_t = man(sx, sy, tx, ty)
        val = -d_t * 10 + d_o * 0.2
        # small tie-break: avoid wasting steps
        val += (cur_d_t - d_t) * 2
        if bestm is None or val > bestm[0]:
            bestm = (val, dx, dy)
    return [int(bestm[1]), int(bestm[2])]