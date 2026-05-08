def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    safe_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            safe_moves.append((dx, dy, nx, ny))
    if not safe_moves:
        return [0, 0]

    if not resources:
        # Hold position unless it improves distance to opponent (avoid stepping into dead zones)
        best = None
        for dx, dy, nx, ny in safe_moves:
            d = man(nx, ny, ox, oy)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Pick target with largest "lead" (we arrive earlier), tie-break by nearer + resource "density" (closer to other resources).
    best_t = None
    for rx, ry in resources:
        myt = man(sx, sy, rx, ry)
        ot = man(ox, oy, rx, ry)
        lead = ot - myt  # positive means we reach first
        density = 0
        for r2x, r2y in resources:
            if (r2x, r2y) != (rx, ry) and man(rx, ry, r2x, r2y) <= 2:
                density += 1
        key = (lead, -myt, density, -((rx + ry) % 2), -rx, -ry)
        if best_t is None or key > best_t[0]:
            best_t = (key, (rx, ry), myt, ot)
    (rx, ry) = best_t[1]

    # Move one step to reduce distance to chosen target; if opponent threatens closer resource, switch.
    def threat_score():
        best = None
        for tx, ty in resources:
            myt = man(sx, sy, tx, ty)
            ot = man(ox, oy, tx, ty)
            lead = ot - myt
            key = (lead, -myt)
            if best is None or key > best[0]:
                best = (key, (tx, ty))
        return best

    # Look-ahead: if we can't keep lead at next step, choose alternative target that we can.
    best_move = None
    for dx, dy, nx, ny in safe_moves:
        my_next = man(nx, ny, rx, ry)
        ot_now = man(ox, oy, rx, ry)
        lead_next = ot_now - my_next
        # Evaluate if there exists a better target we can secure next.
        best_secure_key = None
        for tx, ty in resources:
            myt = man(nx, ny, tx, ty)
            ot = man(ox, oy, tx, ty)
            lead = ot - myt
            key = (lead, -myt, -((tx + ty) % 2), -tx, -ty)
            if best_secure_key is None or key > best_secure_key:
                best_secure_key = key
        # Primary: keep/extend lead; Secondary: get closer to target; Tertiary: avoid unnecessary movement.
        key = (lead_next, best_secure_key[0], -my_next, -((nx + ny) % 2), abs(dx) + abs(dy))
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)

    return [int(best_move[1]), int(best_move[2])]