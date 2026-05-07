def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
        except Exception:
            pass

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    best = None
    best_score = -10**18

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if resources:
        target = min(resources, key=lambda t: manhattan((sx, sy), t))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        score = 0
        if resources:
            dres = manhattan((nx, ny), target)
            score += 1000 - dres * 20
        dopp = manhattan((nx, ny), (ox, oy))
        score += (dopp * 10)
        if (nx, ny) == (ox, oy):
            score -= 10**6
        if (nx, ny) in resources:
            score += 10**6

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best