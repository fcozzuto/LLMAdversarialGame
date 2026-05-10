def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    unclaimed = observation.get("unclaimed_cells") or []

    def score_target(tx, ty):
        ds = abs(tx - sx) + abs(ty - sy)
        do = abs(tx - ox) + abs(ty - oy)
        edge = 1 if (tx == 0 or tx == w - 1 or ty == 0 or ty == h - 1) else 0
        # Prefer targets where we are closer than opponent; tie-break toward edges and higher coordinates.
        return (do - ds) * 1000 + edge * 5 - (tx + ty)

    target = None
    best = -10**18
    for tx, ty in resources:
        v = score_target(tx, ty)
        if v > best or (v == best and (tx, ty) < target):
            best, target = v, (tx, ty)
    if target is None and unclaimed:
        for tx, ty in unclaimed:
            x, y = int(tx), int(ty)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                v = score_target(x, y)
                if v > best or (v == best and (x, y) < target):
                    best, target = v, (x, y)
    if target is None:
        target = (w // 2, h // 2)

    tx, ty = target
    moves = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    bestm = (0, 0)
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        ds = abs(tx - nx) + abs(ty - ny)
        do = abs(tx - ox) + abs(ty - oy)
        v = (do - ds) * 1000 - ds
        # Avoid walking into opponent by making it worse if we move closer to them.
        v -= (abs(nx - ox) + abs(ny - oy)) // 2
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv, bestm = v, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]