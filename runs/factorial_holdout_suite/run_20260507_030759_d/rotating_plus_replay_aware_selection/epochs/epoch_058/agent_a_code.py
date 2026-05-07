def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def t(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = None
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue

        # If opponent is closer to everything, we still pick a move that maximizes our "first-claim" advantage.
        best_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            so = t(nsx, nsy, rx, ry)
            oo = t(ox, oy, rx, ry)
            # Primary: how much sooner we arrive than opponent (positive is good).
            adv = oo - so
            # Secondary: prefer faster arrival; tertiary: prefer center-of-board slightly for stability.
            center_bias = -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2)
            val = adv * 1000 - so * 5 + center_bias * 0.01
            if best_for_move is None or val > best_for_move:
                best_for_move = val

        # Small deterministic preference: if tied, choose lexicographically smaller move.
        key = (-best_for_move, mdx, mdy)
        if best_val is None or key < best_val:
            best_val = key
            best = (mdx, mdy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]