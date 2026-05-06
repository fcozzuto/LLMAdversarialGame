def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    # Choose a resource where we have a distance advantage; otherwise minimize our time while limiting opponent progress.
    best = None
    best_key = None
    opp_close = king_dist(sx, sy, ox, oy) <= 2
    if resources:
        for rx, ry in resources:
            ds = king_dist(sx, sy, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            # Prefer advantage; if no advantage, prefer making opponent farther while we still progress.
            key = (-(adv > 0), -adv, ds + 0.35 * do, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
    else:
        best = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = best

    # If opponent is too close, first step: keep distance while still moving toward target.
    cur_do = king_dist(sx, sy, ox, oy)
    best_move = None
    best_val = None
    for dx, dy, nx, ny in valid:
        ns = king_dist(nx, ny, tx, ty)
        nd = king_dist(nx, ny, ox, oy)
        # Main objective: reduce our distance to target, but deny opponent closeness when they are nearby.
        v = 4.0 * ns + 0.8 * (0 if not opp_close else (cur_do - nd)) + 0.25 * nd
        # If we can increase opponent distance meaningfully, reward it more aggressively.
        if opp_close:
            v -= 1.8 * (nd - cur_do)
        # Secondary: avoid moves that place us closer to opponent when we are not making progress.
        if ns >= king_dist(sx, sy, tx, ty):
            v += 0.8 * (2 - min(2, nd))
        # Tie-break deterministically.
        tie = (v, dx, dy, nx, ny)
        if best_val is None or tie < best_val:
            best_val = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]