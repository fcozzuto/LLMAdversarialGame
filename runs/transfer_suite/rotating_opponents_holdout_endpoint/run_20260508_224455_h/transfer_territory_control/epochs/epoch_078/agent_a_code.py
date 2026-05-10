def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obst = set()
    for c in observation.get("obstacles") or []:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    def toset(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))

    opp_pos = observation.get("opponent_position") or None
    ox = oy = None
    if isinstance(opp_pos, (list, tuple)) and len(opp_pos) >= 2:
        ox, oy = int(opp_pos[0]), int(opp_pos[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    best_dx, best_dy = 0, 0
    best = -10**18

    if resources:
        rx0, ry0 = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        rx0 = ry0 = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 6
        if (nx, ny) in selfT:
            score += 2
        if (nx, ny) in oppT:
            score -= 10
        if ox is not None:
            score += -0.2 * (abs(nx - ox) + abs(ny - oy))
        if rx0 is not None:
            score += -1.0 * (abs(nx - rx0) + abs(ny - ry0))
        if score > best or (score == best and (dx, dy) < (best_dx, best_dy)):
            best = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]