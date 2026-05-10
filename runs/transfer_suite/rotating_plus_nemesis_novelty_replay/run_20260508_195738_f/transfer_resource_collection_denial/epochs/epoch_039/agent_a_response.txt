def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (dist(ox, oy, c[0], c[1]), -dist(sx, sy, c[0], c[1])))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if inb(sx + dx, sy + dy): return [dx, dy]
        if inb(sx + dx, sy): return [dx, 0]
        if inb(sx, sy + dy): return [0, dy]
        return [0, 0]

    # Target selection: race resources where we are closer than opponent; also prefer nearer ones.
    best = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        val = (od - sd, -sd)  # maximize advantage, then minimize our distance
        if best is None or val > best[0]:
            best = (val, rx, ry)
    _, tx, ty = best

    # Candidate moves (including stay), prefer moves that reduce our distance while not increasing opponent too much.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                ns = dist(nx, ny, tx, ty)
                no = dist(nx, ny, ox, oy)
                # primary: reduce distance to target; secondary: keep opponent farther
                candidates.append((ns, -no, abs(dx) + abs(dy), dx, dy))
    candidates.sort()
    return [candidates[0][3], candidates[0][4]] if candidates else [0, 0]