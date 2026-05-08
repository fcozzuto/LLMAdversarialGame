def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for nx, ny in [(sx, sy), (0, 0), (1, 0), (0, 1), (1, 1)]:
            nx, ny = int(nx), int(ny)
            if ok(nx, ny):
                sx, sy = nx, ny
                break
        else:
            return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    targets = resources if resources else unclaimed
    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    bestv = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist_op = abs(nx - ox) + abs(ny - oy)
        if targets:
            dist_t = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            # Prefer reaching targets quickly; slightly prefer staying away from opponent.
            v = -dist_t * 100 - dist_op
        else:
            # No targets: expand territory by moving away from opponent.
            v = dist_op
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]