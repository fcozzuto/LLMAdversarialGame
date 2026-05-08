def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed:
        unclaimed = set(resources)

    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    remaining = observation.get("remaining_resource_count", None)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x, y, a, b): return abs(x - a) + abs(y - b)

    targets = []
    if resources:
        targets.append(("res", resources))
    if unclaimed:
        targets.append(("uncl", unclaimed))
    if not targets and oppT:
        targets.append(("opp", oppT))

    # Prefer nearest resource; otherwise nearest unclaimed that is near opponent; else move towards opponent.
    best_target = None
    best_key = None
    for kind, cells in targets:
        for x, y in cells:
            if not inb(x, y):
                continue
            if (x, y) in obstacles:
                continue
            d = man(sx, sy, x, y)
            adj_op = 1 if oppT and any((x + dx, y + dy) in oppT for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]) else 0
            # Deterministic key: smaller is better
            key = (
                0 if kind == "res" else (1 if kind == "uncl" else 2),
                0 if adj_op else 1,
                d,
                x,
                y,
            )
            if best_key is None or key < best_key:
                best_key = key
                best_target = (x, y, kind)

    tx, ty, _ = best_target if best_target else (ox, oy, "opp")

    # Evaluate moves; avoid obstacles/out of bounds; tie-break by dir order.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in selfT:
            tpen = 0
        else:
            tpen = -1  # prefer leaving territory to claim
        # If no unclaimed/resources, chase opponent.
        chase = 0 if best_target and best_target[2] in ("res", "uncl") else 1
        d = man(nx, ny, tx, ty)
        opp_d = man(nx, ny, ox, oy)
        # Higher score is better
        score = (-d, tpen, opp_d, nx, ny, chase)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]