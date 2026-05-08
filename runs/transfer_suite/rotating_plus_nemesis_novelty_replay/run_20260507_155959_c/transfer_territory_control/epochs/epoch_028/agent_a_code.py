def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unclaimed = observation.get("unclaimed_cells", []) or []
    unclaimed_cells = []
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed_cells.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target():
        if not unclaimed_cells:
            return None
        best = None
        for x, y in unclaimed_cells:
            d = abs(x - sx) + abs(y - sy)
            od = abs(x - ox) + abs(y - oy)
            # Prefer closer to us, farther from opponent; deterministic tie-break by coordinates
            key = (d, -od, x, y)
            if best is None or key < best[0]:
                best = (key, (x, y))
        return best[1]

    target = best_target()

    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            tx, ty = target
            d_to_t = abs(nx - tx) + abs(ny - ty)
            d_to_o = abs(nx - ox) + abs(ny - oy)
            key = (d_to_t, -d_to_o, dx, dy)
        else:
            # No unclaimed: drift away from opponent, then toward bottom-right deterministically
            d_to_o = abs(nx - ox) + abs(ny - oy)
            key = (-d_to_o, -nx, -ny, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move