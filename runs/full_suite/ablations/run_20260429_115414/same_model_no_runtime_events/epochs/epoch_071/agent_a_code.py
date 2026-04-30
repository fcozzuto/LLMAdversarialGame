def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target where we are (deterministically) faster than opponent.
    best = None
    best_sd = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd  # larger => we are sooner
        key = (gap, -sd, -cheb(ox, oy, sx, sy), -rx - ry)  # deterministic tie-breaks
        if best is None or key > best_key:
            best = (rx, ry)
            best_sd = sd
            best_key = key

    tx, ty = best

    # Choose step that keeps/expands our advantage; tie-break toward smaller our distance to target.
    chosen = (0, 0)
    best_step_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)  # opponent assumed static for one-step choice
        gap = nod - nsd
        step_key = (gap, -nsd, -(abs(ox - nx) + abs(oy - ny)), -dx, -dy)
        if best_step_key is None or step_key > best_step_key:
            best_step_key = step_key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]