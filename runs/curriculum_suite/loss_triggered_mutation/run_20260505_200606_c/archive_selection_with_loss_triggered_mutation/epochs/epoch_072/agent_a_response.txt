def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def step_score(nx, ny, target):
        tx, ty = target
        dme = man(nx, ny, tx, ty)
        dop = man(nx, ny, ox, oy)
        return (dop - dme) * 10 - dme - dop * 0.05

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy) * 2 - man(nx, ny, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
                bestv = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_target = None
    best_t = None
    for rx, ry in resources:
        dme = man(sx, sy, rx, ry)
        dop = man(ox, oy, rx, ry)
        # Prefer resources we can reach first, and those that also deny opponent.
        v = (dop - dme) * 10 - dme
        if best_t is None or v > best_t or (v == best_t and dme < man(sx, sy, best_target[0], best_target[1])):
            best_t = v
            best_target = (rx, ry)

    tx, ty = best_target
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    primary = (desired_dx, desired_dy)
    candidates.append(primary)
    if primary != (0, 0):
        candidates.append((desired_dx, 0))
        candidates.append((0, desired_dy))
    # Fill remaining with deterministic order
    for m in moves:
        if m not in candidates:
            candidates.append(m)

    best_move = (0, 0)
    bestv = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = step_score(nx, ny, (tx, ty))
        # Small tie-break: prefer reducing distance to target.
        v = v * 1000 - man(nx, ny, tx, ty)
        if bestv is None or v > bestv:
            bestv = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]