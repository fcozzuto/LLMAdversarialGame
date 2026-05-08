def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    self_role = observation.get("self_role", "pursuer")

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_min_d2(x, y):
        md = 10**9
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < md:
                md = d
                if md == 0:
                    return 0
        return md if md != 10**9 else 10**6

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best = None
    best_val = None
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)
        center = dist2(nx, ny, cx, cy)

        # Obstacle proximity penalty: prefer squares with more clearance
        md2 = obst_min_d2(nx, ny)
        clear_pen = 0
        if md2 < 4:
            clear_pen = (4 - md2) * 20
        elif md2 < 9:
            clear_pen = (9 - md2) * 6

        # Role-based objective
        if self_role == "pursuer":
            # Chase; also slightly keep toward center to reduce escape lanes
            val = -d - center * 0.02 - clear_pen
        else:
            # Evade; keep distance and drift to corners/edges less likely to be cornered
            # (Favor center escape here is safer against direct pursuit)
            val = d - center * 0.04 - clear_pen

        if best is None or val > best_val:
            best = [dxm, dym]
            best_val = val

    if best is None:
        return [0, 0]
    return best