def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Prefer resources we can reach strictly sooner; otherwise pick best compromise.
    best = None
    best_key = None
    for x, y in resources:
        our_d = man(sx, sy, x, y)
        opp_d = man(ox, oy, x, y)
        adv = opp_d - our_d
        # Key: maximize (our_d < opp_d) and adv; tie-break by smaller our_d then coordinates.
        positive = 1 if adv > 0 else 0
        key = (-positive, -(adv), our_d, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestmd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        # Deterministic tie-break: smallest distance, then preferred dx/dy ordering by list.
        if bestmd is None or d < bestmd:
            bestmd = d
            bestm = (dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]