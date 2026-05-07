def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))

    if not targets:
        return [0, 0]

    # Choose a deterministic main target: closest to self, then tie by coordinates.
    tx, ty = min(targets, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        advantage = opd - myd  # larger is better

        key = (advantage, -myd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return list(best if best is not None else (0, 0))