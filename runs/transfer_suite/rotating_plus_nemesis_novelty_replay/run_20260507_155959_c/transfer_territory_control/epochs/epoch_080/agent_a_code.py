def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for c in (observation.get("unclaimed_cells") or []):
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    targets = unclaimed if unclaimed else resources
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if targets:
            md = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            tscore = -md * 10
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            tscore = - (abs(nx - cx) + abs(ny - cy))

        od = abs(nx - ox) + abs(ny - oy)
        oscore = -od * 2  # prefer staying away from opponent

        score = tscore + oscore + (1 if (nx, ny) in unclaimed else 0)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]