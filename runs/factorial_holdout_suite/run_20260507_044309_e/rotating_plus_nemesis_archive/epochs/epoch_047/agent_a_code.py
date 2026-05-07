def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is None or len(b) < 2:
            continue
        bx, by = int(b[0]), int(b[1])
        if 0 <= bx < w and 0 <= by < h:
            obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            resources.append((rx, ry))

    if (sx, sy) in resources or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    cand_moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a resource we can reach not later than the opponent; otherwise pick best "blocking" option.
    best = None
    best_score = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer immediate wins; otherwise prefer resources that delay/deny opponent.
        lead = do - ds  # positive => we are sooner
        score = (-lead, ds, rx, ry)  # deterministic tie-break
        if best_score is None or score < best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    # Take one step toward target while avoiding stepping onto obstacles if possible.
    dx = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    dy = 0
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    preferred = (dx, dy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    nx, ny = sx + preferred[0], sy + preferred[1]
    if valid(nx, ny):
        return [preferred[0], preferred[1]]

    # Fallback: deterministic best move among valid neighbors by distance to target, then distance to opponent.
    opp_bias = []
    for mx, my in cand_moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_to_o = man(nx, ny, ox, oy)
        opp_bias.append(((d_to_t, -d_to_o, mx, my), [mx, my]))
    if opp_bias:
        opp_bias.sort(key=lambda z: z[0])
        return opp_bias[0][1]

    return [0, 0]