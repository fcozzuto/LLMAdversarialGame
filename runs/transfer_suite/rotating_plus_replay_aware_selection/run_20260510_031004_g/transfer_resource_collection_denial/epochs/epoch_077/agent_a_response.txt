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

    opp_to_me = cheb(ox, oy, sx, sy)
    best = None
    bestv = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Race-first: prefer strictly earlier; otherwise the closest "advantage".
        win_margin = opp_d - my_d
        is_earlier = 1 if my_d < opp_d else 0
        # Slightly prefer resources that are "later" along board to break ties deterministically.
        tie_boost = (rx * 0.001) + (ry * 0.0001)
        # If opponent is already very close to us, prioritize earlier win more strongly.
        early_weight = 2 + (1 if opp_to_me <= 2 else 0)
        v = (is_earlier * early_weight, win_margin, -my_d, -(rx + ry * 0.01) + tie_boost)
        if bestv is None or v > bestv:
            bestv = v
            best = (rx, ry)

    tx, ty = best
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    # Choose the king move that minimizes cheb distance to target; deterministic tie-breaks.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if abs(dx) > 1 or abs(dy) > 1:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((cheb(nx, ny, tx, ty), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], 0 if t[1] == dx0 else 1, 0 if t[2] == dy0 else 1, t[1], t[2]))
    _, mdx, mdy = moves[0]
    return [int(mdx), int(mdy)]