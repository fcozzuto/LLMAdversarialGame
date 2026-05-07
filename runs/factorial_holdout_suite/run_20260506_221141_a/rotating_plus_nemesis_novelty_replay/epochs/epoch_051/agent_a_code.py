def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < gw and 0 <= y < gh:
                obs.add((x, y))

    def dist(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    resources = observation.get("resources") or []
    cand = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obs:
                d1 = dist(sx, sy, x, y)
                d2 = dist(ox, oy, x, y)
                adv = d2 - d1
                cand.append((adv, d1, x, y))
    if not cand:
        return [0, 0]

    cand.sort(reverse=True, key=lambda t: (t[0], -t[1], -t[2]))
    best = cand[0]
    _, _, tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = dist(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
            if dist(nx, ny, tx, ty) <= curd:
                return [dx, dy]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]