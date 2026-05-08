def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in (observation.get("obstacles") or []):
        obs.add((int(p[0]), int(p[1])))

    resources = set()
    for p in (observation.get("resources") or []):
        resources.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        unclaimed.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in (observation.get("self_territory") or []):
        self_terr.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    targets = resources if resources else unclaimed if unclaimed else self_terr
    order = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    best = None
    best_sc = -10**18

    for dx, dy in order:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        sc = 0
        if (nx, ny) in resources:
            sc += 1000
        if (nx, ny) in unclaimed:
            sc += 200
        if (nx, ny) in self_terr:
            sc += 20

        if (nx, ny) in resources:
            sc -= d2(nx, ny, ox, oy) * 0.001
        elif targets:
            tx, ty = min(targets, key=lambda t: d2(nx, ny, t[0], t[1]))
            sc += 50 - d2(nx, ny, tx, ty) * 0.02

        sc -= d2(nx, ny, ox, oy) * 0.01
        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        for dx, dy in order:
            nx, ny = int(sx + dx), int(sy + dy)
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best