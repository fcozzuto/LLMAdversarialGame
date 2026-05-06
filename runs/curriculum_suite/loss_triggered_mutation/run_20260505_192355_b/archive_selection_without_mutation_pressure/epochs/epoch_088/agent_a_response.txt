def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = w // 2, h // 2

    best = None
    best_key = None
    for rx, ry in resources:
        md = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        advantage = od - md  # bigger => we are closer
        edge_pen = (rx == 0) + (ry == 0) + (rx == w - 1) + (ry == h - 1)
        center_bonus = -(abs(rx - cx) + abs(ry - cy))
        # Prefer big advantage; if tied, go for closer and slightly more central.
        key = (advantage, -md, edge_pen, center_bonus)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = manh(nx, ny, tx, ty)
        od = manh(ox, oy, tx, ty)
        advantage_next = od - nd
        # Tie-break: closer to target, then avoid edges, then deterministic.
        edge_pen = (nx == 0) + (ny == 0) + (nx == w - 1) + (ny == h - 1)
        key = (advantage_next, -nd, -edge_pen, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]