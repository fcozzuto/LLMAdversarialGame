def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    tr = observation.get("turns_remaining", 0)
    rem = observation.get("remaining_resource_count", None)
    if rem is None:
        rem = len(resources)
    few = (tr <= 5) or (rem <= 3)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    best = None
    bestv = -10**18
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        margin = od - sd
        v = margin * 3 - sd * (0.25 if not few else 0.65)
        if sd == 0:
            v += 50
        elif sd == 1:
            v += 10
        # Encourage axis progress to fight row-sweep opponents
        if (rx == sx) or (ry == sy):
            v += 1.5
        if v > bestv:
            bestv = v
            best = (rx, ry)

    tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Prefer direct diagonal/axis step; if blocked, pick best alternative toward target.
    preferred = []
    if dx != 0 and dy != 0:
        preferred.append([dx, dy])
    preferred.append([dx, 0])
    preferred.append([0, dy])
    preferred.append([0, 0])
    # Fill remaining deterministic options
    for px in (-1, 0, 1):
        for py in (-1, 0, 1):
            if [px, py] not in preferred:
                preferred.append([px, py])

    target_dist_best = 10**9
    chosen = [0, 0]
    for mx, my in preferred:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d2t = man(nx, ny, tx, ty)
        # Tie-break: prefer not worsening relative to opponent.
        rel = man(nx, ny, tx, ty) - man(ox, oy, tx, ty)
        key = (d2t, rel)
        if key < (target_dist_best, -10**9):
            target_dist_best = d2t
            chosen = [mx, my]

    return [int(chosen[0]), int(chosen[1])]