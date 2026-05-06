def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                rlist.append((rx, ry))
    if not rlist:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Choose move that maximizes our "lead": (opp nearest distance - our nearest distance),
    # plus a small tie-break for reducing our nearest distance.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        our_best = 10**9
        opp_best = 10**9
        for rx, ry in rlist:
            d1 = md(nx, ny, rx, ry)
            if d1 < our_best: our_best = d1
            d2 = md(ox, oy, rx, ry)
            if d2 < opp_best: opp_best = d2

        # Lead prefers larger difference; tie-break prefers smaller our_best; and
        # slight preference for moving toward center of grid to avoid edge stalls.
        center_pen = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        score = (opp_best - our_best) * 100 - our_best - int(center_pen)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]