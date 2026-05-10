def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or role.endswith("e")

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d_old = dist2(sx, sy, ox, oy)
        d_new = dist2(nx, ny, ox, oy)

        wall_pen = 0
        # Prefer moves that don't get "sandwiched" against boundaries/obstacles.
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + adx, ny + ady
            if not safe(tx, ty):
                wall_pen += 1

        center_pen = abs(nx - cx) + abs(ny - cy)
        center_term = -0.02 * center_pen

        # Deterministic tie-break by move order already fixed.
        if is_evader:
            # Run to maximize separation; also avoid boundaries/walls.
            sc = (d_new - d_old) + (-0.35 * wall_pen) + center_term
        else:
            # Pursuer: reduce separation; also avoid being blocked into walls.
            sc = (d_old - d_new) + (-0.35 * wall_pen) + center_term

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best