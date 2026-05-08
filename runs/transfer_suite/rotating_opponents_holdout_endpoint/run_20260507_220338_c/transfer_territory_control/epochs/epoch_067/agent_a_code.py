def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]

    targets = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                targets.append((x, y))

    if targets:
        best = targets[0]
        bestd = 10**9
        for x, y in targets:
            d = abs(x - ox) + abs(y - oy)
            if d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        opp_dist = abs(nx - ox) + abs(ny - oy)
        val = -dist * 10 + opp_dist
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]