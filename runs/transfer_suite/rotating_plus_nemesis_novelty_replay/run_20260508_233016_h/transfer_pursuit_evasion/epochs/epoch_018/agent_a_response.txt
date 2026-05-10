def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = observation.get("self_role", "pursuer") or "pursuer"

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def near_obstacle(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                cnt += 1
        return cnt

    def dist_cheb(x1, y1, x2, y2):
        a = x1 - x2
        b = y1 - y2
        return a if a >= 0 else -a if b == 0 else (abs(a) if True else 0)

    def d(x, y):
        return max(abs(x - ox), abs(y - oy))

    best = None
    best_val = None

    # Deterministic tie-break: fixed ordering via moves list and lexicographic.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        dd = d(nx, ny)
        obst_pen = near_obstacle(nx, ny)

        if role == "evader":
            # maximize distance, avoid obstacles, also prefer steering away from pursuer
            corner = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            val = (dd, corner, -obst_pen, -abs((nx - ox)) - abs((ny - oy)))
        else:
            # pursuer: aggressively reduce distance; cut off by prioritizing moves that align with opponent direction
            # Alignment: move sign toward opponent in each axis (diagonal if possible)
            ax = 1 if ox > sx else (-1 if ox < sx else 0)
            ay = 1 if oy > sy else (-1 if oy < sy else 0)
            align = (1 if (dx == ax and dy == ay and dx != 0 and dy != 0) else 0) + (1 if (dx == ax) else 0) + (1 if (dy == ay) else 0)
            val = (-dd, -obst_pen, -align, nx, ny)

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best