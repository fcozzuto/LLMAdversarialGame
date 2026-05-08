def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target where we are (ideally) ahead; otherwise minimize being behind.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # prioritize (sd-od) smallest (most negative); tie: smaller sd then lex
        key = (sd - od, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    rx, ry = best[1]

    # Local move: minimize resulting (sd-od) to that target; tie: smaller sd, then prefer dx toward rx, dy toward ry.
    best_m = None
    target_x_dir = 0 if rx == sx else (1 if rx > sx else -1)
    target_y_dir = 0 if ry == sy else (1 if ry > sy else -1)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nsd = man(nx, ny, rx, ry)
        nod = man(ox, oy, rx, ry)
        key = (nsd - nod, nsd, -(dx == target_x_dir), -(dy == target_y_dir), dx, dy)
        if best_m is None or key < best_m[0]:
            best_m = (key, (dx, dy))
    return [best_m[1][0], best_m[1][1]]