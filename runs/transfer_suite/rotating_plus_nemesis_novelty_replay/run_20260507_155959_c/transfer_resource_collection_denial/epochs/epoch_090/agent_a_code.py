def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dist_self_opp = abs(nx - ox) + abs(ny - oy)

        if resources:
            rbest = None
            rdist = None
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rx, ry = r[0], r[1]
                    if isinstance(rx, int) and isinstance(ry, int) and 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                        d = abs(nx - rx) + abs(ny - ry)
                        if rdist is None or d < rdist or (d == rdist and (rx, ry) < rbest):
                            rdist = d
                            rbest = (rx, ry)
            if rdist is None:
                score = (0, dist_self_opp)
            else:
                score = (-rdist, dist_self_opp)
        else:
            score = (0, dist_self_opp)

        if best is None or score > bestv:
            bestv = score
            best = (dx, dy)

    return [best[0], best[1]]