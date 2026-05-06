def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    def nearest_from(x, y, whox, whoy):
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = md(x, y, rx, ry)
            od = md(whox, whoy, rx, ry)
            # Prefer resources we can arrive to no later than opponent; otherwise, penalize heavily.
            adv = (od - sd)
            key = (-(od <= sd + 0), -adv, sd, od, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry, sd, od, adv)
        return best[1], best[2], best[3], best[4], best[5]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves if moves else [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        _, _, sd, od, adv = nearest_from(nx, ny, ox, oy)

        # Extra: avoid getting closer to a single opponent-targeted resource too easily.
        # Compute opponent's nearest resource distance.
        opp_near_sd = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = md(ox, oy, rx, ry)
            if opp_near_sd is None or d < opp_near_sd:
                opp_near_sd = d

        # Value: maximize advantage, then prefer smaller self distance, then discourage moving toward opponent's nearest region.
        toward_opponent = md(nx, ny, ox, oy)
        val = (-(adv <= 0), -adv, sd, toward_opponent, -opp_near_sd, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]