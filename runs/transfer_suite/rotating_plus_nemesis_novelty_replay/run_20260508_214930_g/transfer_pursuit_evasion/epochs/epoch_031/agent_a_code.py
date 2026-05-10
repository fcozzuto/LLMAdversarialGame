def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for b in (observation.get("obstacles", []) or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((int(b[0]), int(b[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if resources:
            dres = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dres = 0
        dopp = manh(nx, ny, ox, oy)
        cand = (dres, -dopp, nx, ny)
        if best is None or cand < best:
            best = cand
            best_move = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best_move