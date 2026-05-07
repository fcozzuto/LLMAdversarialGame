def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = ox, oy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        if valid(sx + dx, sy):
            return [dx, 0]
        if valid(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    best_move = [0, 0]
    best_val = None
    rem = int(observation.get("remaining_resource_count") or len(resources))

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        # Choose the resource that this move would most improve relative to the opponent
        chosen = None
        chosen_key = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; also break ties by closer distance
            key = (myd - opd, myd, -opd, rx, ry)
            if chosen_key is None or key < chosen_key:
                chosen_key = key
                chosen = (rx, ry)
        # Evaluate move using chosen resource advantage and slight preference for faster collection early
        rx, ry = chosen
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        val = (myd - opd, myd + (rem * 0.01), -opd)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move