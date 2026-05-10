def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p
            blocked.add((int(x), int(y)))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    targets = []

    if unclaimed:
        cells = []
        for c in unclaimed:
            if isinstance(c, (list, tuple)) and len(c) == 2:
                x, y = int(c[0]), int(c[1])
                if inside(x, y) and (x, y) not in blocked:
                    cells.append((x, y))
        cells.sort()
        cells = cells[:25]
        targets = cells
    elif resources:
        cells = []
        for c in resources:
            if isinstance(c, (list, tuple)) and len(c) == 2:
                x, y = int(c[0]), int(c[1])
                if inside(x, y) and (x, y) not in blocked:
                    cells.append((x, y))
        cells.sort()
        cells = cells[:25]
        targets = cells
    else:
        if inside(ox, oy) and (ox, oy) not in blocked:
            targets = [(ox, oy)]
        else:
            targets = [(sx, sy)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        md = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < md:
                md = d
        # Encourage staying closer to our immediate aim and (when targets are not present) approaching opponent
        opp_bias = -man(nx, ny, ox, oy) * (1 if not unclaimed and not resources else 0.1)
        score = -md + opp_bias
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]