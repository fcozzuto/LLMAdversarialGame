def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource that we are likely to beat (self distance < opponent distance).
    target = None
    best = -10**18
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we can reach sooner, strongly prefer; otherwise, avoid unless it's very close.
            lead = do - ds
            score = 0
            if lead > 0:
                score = 2000 * lead - 5 * ds
            else:
                score = -30 * ds + 2 * lead  # small penalty, but discourages races
            # Mild preference for mid-board to reduce corner traps.
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            center_bias = - (abs(rx - cx) + abs(ry - cy))
            score += center_bias
            if score > best:
                best = score
                target = (rx, ry)
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = int(target[0]), int(target[1])

    # Greedy step to reduce distance to target, with safety: don't step into being strictly worse vs opponent.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_now = cheb(sx, sy, tx, ty)
        # Favor progress; small extra if it also increases the lead over opponent to the same target.
        opp_d = cheb(ox, oy, tx, ty)
        lead_new = opp_d - d_self
        val = 100 * (d_now - d_self) + 50 * lead_new - 0.1 * (d_self)
        if (nx, ny) == (tx, ty):
            val += 10000
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move