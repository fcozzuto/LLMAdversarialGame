def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    if not resources:
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dmy = dist(nx, ny, sx, sy)
            dop = dist(nx, ny, ox, oy)
            v = dop * 3 - dmy
            if v > bestv or (v == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    # Pick the move that most improves relative closeness to a promising resource.
    best, bestv = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = -dist(nx, ny, ox, oy)  # prefer staying away from opponent a bit
        # Greedy over resources: maximize opponent-relative improvement to nearest resource.
        for tx, ty in resources:
            dme = dist(nx, ny, tx, ty)
            dop = dist(ox, oy, tx, ty)
            # Higher is better: I want to be closer than opponent by a lot.
            gain = dop - dme
            v += gain
        if v > bestv or (v == bestv and (dx, dy) < best):
            best, bestv = (dx, dy), v

    return [best[0], best[1]]