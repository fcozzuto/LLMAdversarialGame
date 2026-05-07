def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = (cheb(nx, ny, cx, cy), nx, ny)
            if best is None or v < best[0]:
                best = (v, [dx, dy])
        return best[1] if best is not None else [0, 0]

    def resource_priority(rx, ry):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        return (sd - od, sd, rx, ry)

    target = min(resources, key=lambda c: resource_priority(c[0], c[1]))
    tx, ty = target

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer blocking by reducing (our distance - opponent distance)
        # and avoid stepping away from the target.
        step_score = (sd - od, sd, abs(nx - tx) + abs(ny - ty), -1 if (nx, ny) == target else 0, nx, ny)
        if best is None or step_score < best[0]:
            best = (step_score, [dx, dy])
    return best[1] if best is not None else [0, 0]