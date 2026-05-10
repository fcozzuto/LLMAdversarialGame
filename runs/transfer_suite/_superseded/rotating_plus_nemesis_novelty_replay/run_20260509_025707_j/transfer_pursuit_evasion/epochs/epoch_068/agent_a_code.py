def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    self_is_evader = is_evader(observation.get("self_role"))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # deterministic tie-break order: iterate dirs, keep first best
    best_move = (0, 0)
    best_val = None

    # heuristic corner target
    if self_is_evader:
        # run toward farthest corner from pursuer
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        # pursue toward corner that increases separation from evader (helps against zigzag)
        target_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    tcx, tcy = target_corner

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, tcx, tcy)
        d_corner_now = dist2(sx, sy, tcx, tcy)

        # penalize staying if not optimal (keeps motion deterministic)
        stay_pen = 1 if (nx == sx and ny == sy) else 0

        if self_is_evader:
            # maximize separation; also drift toward chosen far corner
            val = (d_opp * 1000) + (d_corner_now - d_corner) - (stay_pen * 5)
        else:
            # minimize separation; also drift toward chosen corner
            val = (-d_opp * 1000) + (d_corner_now - d_corner) - (stay_pen * 5)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]