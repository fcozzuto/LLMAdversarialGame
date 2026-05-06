def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            # keep distance from opponent while drifting to center
            score = md(nx, ny, cx, cy) - md(nx, ny, ox, oy)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best = None
    for dx, dy, nx, ny in moves:
        # Choose the resource that gives the best duel advantage.
        duel_best = None
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(nx, ny, rx, ry)
            # Primary: maximize (opp_d - our_d). Secondary: minimize our_d.
            # Tertiary: avoid moving closer to opponent when close enough.
            advantage = opp_d - our_d
            tie = (our_d, md(nx, ny, ox, oy))
            val = (advantage, -tie[0], -tie[1])
            if duel_best is None or val > duel_best:
                duel_best = val

        # Additional bias against sweep-row pressure: prefer moves that change both coordinates if possible.
        coord_mix = (1 if dx != 0 and dy != 0 else 0)
        key = (duel_best[0], duel_best[1], duel_best[2], coord_mix, -(md(nx, ny, ox, oy)))
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]