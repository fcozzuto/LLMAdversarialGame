def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turns_remaining = int(observation.get("turns_remaining") or 0)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        if sd > turns_remaining + 1:
            continue
        # Prefer contestable resources; if not contestable, pick those far from opponent.
        contestable = 1 if sd <= od else 0
        key = (contestable, abs(od - sd), od, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    dxs = 0 if tx == sx else (1 if tx > sx else -1)
    dys = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((man(nx, ny, tx, ty), abs(dx - dxs) + abs(dy - dys), - (abs(nx - ox) + abs(ny - oy)), dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][4])]