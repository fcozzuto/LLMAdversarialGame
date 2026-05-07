def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def score_cell(rx, ry):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        return (od - sd, -sd)  # prefer we arrive first, then closer

    target = resources[0]
    best = score_cell(target[0], target[1])
    for rx, ry in resources[1:]:
        sc = score_cell(rx, ry)
        if sc > best:
            best = sc
            target = (rx, ry)

    tx, ty = target

    best_move = [0, 0]
    best_next = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            cur = (man(nx, ny, tx, ty), man(nx, ny, ox, oy) - man(nx, ny, sx, sy))
            if best_next is None or cur < best_next:
                best_next = cur
                best_move = [dx, dy]
    return best_move