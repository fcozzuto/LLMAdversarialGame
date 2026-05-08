def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def to_list(v):
        out = []
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.append((int(p[0]), int(p[1])))
        return out

    resources = to_list(observation.get("resources"))
    unclaimed = to_list(observation.get("unclaimed_cells"))
    opp_territory = set(to_list(observation.get("opponent_territory")))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    target = None
    if resources:
        best = min(resources, key=lambda p: dist2(sx, sy, p[0], p[1]))
        target = best
    elif unclaimed:
        best = min(unclaimed, key=lambda p: dist2(sx, sy, p[0], p[1]))
        target = best
    else:
        target = (ox, oy)

    best_move = deltas[0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        score = -dist2(nx, ny, target[0], target[1]) + 0.1 * dist2(nx, ny, ox, oy)
        if (nx, ny) in opp_territory:
            score += 5000
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]