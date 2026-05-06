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

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If resources are few, prioritize blocking by moving to tiles that make opponent paths worse
    # Score each candidate move by "resource advantage" after moving.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        if res:
            # For each resource, compute advantage: (opp_dist - my_dist).
            # Higher is better; also slightly prefer closer to some resource and farther from opponent.
            best_adv = None
            best_res = None
            for rx, ry in res:
                myd = dist(nx, ny, rx, ry)
                opd = dist(ox, oy, rx, ry)
                # Block/intercept pressure: if opponent is already closer, reduce its advantage.
                adv = opd - myd
                key = (adv, -opd, -myd, rx, ry)
                if best_adv is None or key > best_adv:
                    best_adv = key
                    best_res = (rx, ry, myd, opd, adv)
            rx, ry, myd, opd, adv = best_res
            # Encourage capturing when we're not behind; discourage falling into opponent's immediate vicinity.
            myd_term = -myd
            opp_term = dist(nx, ny, ox, oy)
            # Strongly prefer moving that reduces opponent's ability to capture soon.
            cap_pressure = -max(0, opd - myd)
            tie_det = (rx, ry, dx, dy)
            key = (adv, myd_term, cap_pressure, opp_term, -dx, -dy, tie_det)
        else:
            # No visible resources: move to maximize distance from opponent (static guard fallback)
            key = (dist(nx, ny, ox, oy), -nx, -ny, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]