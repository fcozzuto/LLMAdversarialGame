def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    rem = int(observation.get("turns_remaining", 0) or 0)

    best_t = resources[0]
    best_v = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Front-run score: strongly prefer resources where we can arrive not later than opponent.
        # If both are similar, prefer fewer self steps (earlier collection).
        v = (od - sd) * 4 - sd
        if sd > od:
            v -= 8
        # Slight urgency: later in game, prioritize closer targets.
        v -= (rem > 0 and sd > rem / 3) * 2
        if best_v is None or v > best_v or (v == best_v and (tx < best_t[0] or (tx == best_t[0] and ty < best_t[1]))):
            best_v = v
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_ms = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Move quality: minimize our distance; avoid giving opponent a gain.
        ms = (no - ns) * 3 - ns
        if best_ms is None or ms > best_ms:
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]