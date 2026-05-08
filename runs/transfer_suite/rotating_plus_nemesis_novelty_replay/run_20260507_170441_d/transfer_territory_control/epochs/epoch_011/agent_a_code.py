def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                blocked.add((x, y))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells", []) or []
    resources = observation.get("resources", []) or []
    targets = unclaimed if unclaimed else resources
    if not targets:
        return [0, 0]

    tlist = []
    for p in targets:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) != (sx, sy) and (x, y) not in blocked:
                tlist.append((x, y))
        except:
            pass
    if not tlist:
        return [0, 0]

    def mindist(x, y):
        best = None
        for tx, ty in tlist:
            d = abs(tx - x) + abs(ty - y)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked or (nx, ny) == (ox, oy):
            continue
        d_to = mindist(nx, ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        key = (d_to, -d_opp, abs(dx) + abs(dy))
        if best is None or key < best:
            best = key
            best_move = [dx, dy]
    return best_move