def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        sx, sy = w // 2, h // 2
        if not ok(sx, sy):
            return [0, 0]

    targets = []
    for t in unclaimed:
        if ok(t[0], t[1]) and (t not in self_terr):
            targets.append(t)
    for t in opp_terr:
        if ok(t[0], t[1]) and (t not in self_terr):
            targets.append(t)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    tx, ty = w // 2, h // 2
    if targets:
        scored = []
        for x, y in targets:
            d0 = dist((sx, sy), (x, y))
            d1 = dist((ox, oy), (x, y))
            scored.append((d0 - 0.2 * d1, d0, x, y))
        scored.sort()
        tx, ty = scored[0][2], scored[0][3]
    elif unclaimed:
        # deterministic fallback
        tx, ty = sorted(unclaimed)[0]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Prefer moving closer to target; slightly prefer increasing to unclaimed.
        score = abs(nx - tx) + abs(ny - ty)
        if (nx, ny) in unclaimed:
            score -= 0.15
        if (nx, ny) in opp_terr:
            score -= 0.05
        if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    return list(best[1]) if best else [0, 0]