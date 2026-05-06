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

    if resources:
        # Pick a resource where we are relatively closer than opponent
        best_t = None
        best_gap = None
        for rx, ry in resources:
            our_d = md(sx, sy, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            gap = opp_d - our_d  # bigger => advantage
            # Slight preference for nearer resources when gap ties
            key = (gap, -(our_d))
            if best_t is None or key > best_t[0]:
                best_t = (key, (rx, ry))
                best_gap = gap
        _, (tx, ty) = best_t
    else:
        # No visible resources: drift to center while keeping distance
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    for dx, dy, nx, ny in moves:
        our_d = md(nx, ny, tx, ty)
        opp_d = md(ox, oy, tx, ty)
        dist_agents = md(nx, ny, ox, oy)

        # Evaluate move: approach target, maintain distance, avoid giving opponent an advantage
        # (use predicted our_d after move vs current opp_d)
        score = 10 * our_d - 6 * dist_agents + 3 * (opp_d - our_d)
        # If stepping would reduce our distance and also prevent being cornered, score improves
        if best is None or score < best[0] or (score == best[0] and our_d < best[2]):
            best = (score, dx, dy, our_d)

    return [int(best[1]), int(best[2])]