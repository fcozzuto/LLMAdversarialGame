def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    # Prefer a corner farthest from opponent, ties by deterministic order
    tx, ty = corners[0]
    bestd = -1
    for cx, cy in corners:
        d = abs(cx - (w-1-ox)) + abs(cy - (h-1-oy))
        if d > bestd or (d == bestd and (cx, cy) < (tx, ty)):
            bestd = d
            tx, ty = cx, cy

    # If unclaimed_cells exists, bias toward the closest unclaimed to that corner
    unclaimed = observation.get("unclaimed_cells") or []
    if unclaimed:
        target = None
        tbest = None
        for c in unclaimed:
            try:
                x, y = int(c[0]), int(c[1])
            except:
                continue
            if not (0 <= x < w and 0 <= y < h) or (x, y) in blocked:
                continue
            dcorner = abs(x - tx) + abs(y - ty)
            if tbest is None or dcorner < tbest or (dcorner == tbest and (x, y) < target):
                tbest = dcorner
                target = (x, y)
        if target:
            tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        # Lower is better: distance to target, slight preference to move
        score = abs(nx - tx) + abs(ny - ty)
        score = (score * 10) + (0 if (dx == 0 and dy == 0) else 1)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]