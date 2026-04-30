def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if resources:
        best = None
        for rx, ry in resources:
            sd = d2(sx, sy, rx, ry)
            od = d2(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer (maximize od - sd).
            score = (od - sd, -sd)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources visible: head to a deterministic "pressure" square near center.
        cx, cy = (w // 2, h // 2)
        if (sx + sy) % 2 == 0:
            cx = max(0, cx - 1)
        else:
            cy = max(0, cy - 1)
        tx, ty = cx, cy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that reduce distance to target; then reduce distance to opponent (blocking).
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dv = d2(nx, ny, tx, ty)
        ob = d2(nx, ny, ox, oy)
        # Small tie-break: favor diagonal when it helps.
        diag_bonus = 1 if dx != 0 and dy != 0 else 0
        val = (dv, -diag_bonus, ob)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]