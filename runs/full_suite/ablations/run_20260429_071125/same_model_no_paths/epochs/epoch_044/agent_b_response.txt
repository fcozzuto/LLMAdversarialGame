def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    if not inb(sx, sy):
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                sx, sy = nx, ny
                break

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Score each resource by how "contested" it is and how good the target is.
    best_res = None
    best_res_score = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        # Prefer resources we are closer to; also avoid giving opponent immediate advantage.
        sc = myd - 1.2 * opd
        # If equal contest, prefer closer to center (adds deterministic bias)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        sc += 0.05 * (abs(rx - cx) + abs(ry - cy))
        if best_res_score is None or sc < best_res_score:
            best_res_score = sc
            best_res = (rx, ry)

    # If no resources, just keep distance from opponent while staying safe
    if best_res is None:
        best_dxdy = (0, 0)
        best_goal = -10**18
        for dx, dy, nx, ny in moves:
            val = cd(nx, ny, ox, oy)
            if val > best_goal:
                best_goal = val
                best_dxdy = (dx, dy)
        return [int(best_dxdy[0]), int(best_dxdy[1])]

    tx, ty = best_res
    # One-step greedy: minimize my distance to target while pushing away from opponent and obstacles naturally via legality.
    best_dxdy = (0, 0)
    best_val = None
    for dx, dy, nx, ny in moves:
        myd = cd(nx, ny, tx, ty)
        opd = cd(nx, ny, ox, oy)
        # Primary: go to target. Secondary: avoid moving closer to opponent.
        val = myd - 0.35 * opd
        # Small deterministic tie-break: prefer moves with larger progress in x, then y toward target.
        val += 0.001 * (abs(tx - nx) + abs(ty - ny))
        if best_val is None or val < best_val:
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]