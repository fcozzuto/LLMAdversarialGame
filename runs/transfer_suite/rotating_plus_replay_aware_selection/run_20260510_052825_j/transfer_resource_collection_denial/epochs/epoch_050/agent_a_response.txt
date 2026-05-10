def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for p in resources:
        x, y = p[0], p[1]
        if inb(x, y) and (x, y) not in obstacles:
            valid.append((x, y))

    if not valid:
        return [0, 0]

    # Pick resource with best estimated advantage to arrive first.
    # If tied, prefer earlier for us and then closer to opponent (less likely they contest later).
    best = None
    for rx, ry in valid:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive means we are earlier
        key = (-adv, sd, od, rx, ry)  # deterministic
        if best is None or key < best[0]:
            best = (key, (rx, ry), sd, od, adv)
    _, (tx, ty), _, _, _ = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Prefer moving to reduce our distance to target while increasing opponent distance.
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # If we can grab immediately (standing on resource), prioritize heavily.
        on_res = (nx, ny) == (tx, ty)
        # Add slight anti-stall: prefer smaller sd2.
        val = (1 if on_res else 0, (od2 - sd2), -sd2)
        # Deterministic tie-break: smallest (dx,dy) lexicographically among equals.
        tieb = (dx, dy)
        if best_val is None or val > best_val or (val == best_val and tieb < best_move):
            best_val = val
            best_move = tieb

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]