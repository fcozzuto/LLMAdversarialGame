def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if any((rx == sx and ry == sy) for rx, ry in resources):
        return [0, 0]

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in cand:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    best_move = None
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # For this move, pick the resource that gives the best relative outcome.
        best_for_move_key = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Primary: maximize advantage (od - sd).
            # Secondary: if tie, prefer smaller our distance to secure pickup earlier.
            # Tertiary: deterministic tie-break by resource position.
            adv = od - sd
            key = (adv, -sd, -(rx * 9 + ry))
            if best_for_move_key is None or key > best_for_move_key:
                best_for_move_key = key

        # Choose the move that maximizes the best resource outcome.
        if best_for_move_key is None:
            continue
        move_key = best_for_move_key
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    if best_move is None:
        for mx, my in cand:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]
    return [best_move[0], best_move[1]]