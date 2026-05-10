def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sp = observation["self_position"]
    op = observation["opponent_position"]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    sr = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in sr)
    if not is_evader:
        if ("pursuer" not in sr) and ("hunter" not in sr) and ("chaser" not in sr):
            # fallback: assume role is pursuer in pursuit_evasion
            is_evader = False

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        # evader: maximize distance to pursuer; also prefer moving toward the farthest corner
        far_corner = max(corners, key=lambda c: max(abs(c[0] - sx), abs(c[1] - sy)) - max(abs(c[0] - ox), abs(c[1] - oy)))
        bc = far_corner[0], far_corner[1]

        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = max(abs(nx - ox), abs(ny - oy))
            corner_bias = - (abs(nx - bc[0]) + abs(ny - bc[1]))
            key = (dist, corner_bias, -nx, -ny)
            if best is None or key > best_key:
                best = (dx, dy)
                best_key = key
        if best is not None:
            return [int(best[0]), int(best[1])]
        return [0, 0]
    else:
        # pursuer: minimize distance to evader; prefer moves that reduce both axes when possible
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = max(abs(nx - ox), abs(ny - oy))
            ax = abs(nx - ox)
            ay = abs(ny - oy)
            # Tie-break: move toward closest axis and toward center to avoid corner escapes by obstacles
            center = (w - 1) / 2.0, (h - 1) / 2.0
            cen_bias = - (abs(nx - center[0]) + abs(ny - center[1]))
            key = (-dist, -(min(ax, ay)), cen_bias, -dx, -dy)
            if best is None or key > best_key:
                best = (dx, dy)
                best_key = key
        if best is not None:
            return [int(best[0]), int(best[1])]
        return [0, 0]