def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diagonal-allowed

    targets = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                sd = dist((sx, sy), (x, y))
                od = dist((ox, oy), (x, y))
                # Prefer resources we can beat; otherwise pick those where we reduce opponent advantage.
                beat = 1_000_000 if sd <= od else 0
                sc = beat + (od - sd) * 80 - sd * 2
                targets.append((sc, x, y))
    if not targets:
        return [0, 0]

    # Deterministic pick: max score, then lowest (x,y) for stability.
    targets.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, tx, ty = targets[0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_m = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = dist((nx, ny), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        # Also consider whether moving to this neighbor improves our ability vs nearby resources.
        # Cheap local proxy: favor reduction of self distance; slight boost if we keep opponent from being closer.
        local = (od - nd) * 5 - nd
        sc = local
        if best is None or sc > best or (sc == best and (dx, dy) < best_m):
            best = sc
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]