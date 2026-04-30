def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Strategic change: choose a "swing" target (prefer resources we can beat),
    # and only then optimize approach; otherwise go for the closest contested.
    scored = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        beat = 1 if sd <= od else 0
        margin = od - sd  # positive means we are closer
        # Tie-break: prefer positions that are relatively far from opponent to reduce contest frequency.
        opp_dist = od
        scored.append((beat, margin, -opp_dist, -sd, rx, ry))
    scored.sort(reverse=True)
    _, _, _, _, tx, ty = scored[0]

    # Move one step toward target with obstacle-avoidance and a slight "shield" from opponent.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = man(nx, ny, tx, ty)
        od2 = man(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: increase distance from opponent; Tertiary: determinism.
        key = (-(nd), od2, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best is None or key > best:
            best = key
    if best is None:
        return [0, 0]
    # Recover dx,dy from key tail
    return [int(best[3]), int(best[4])]