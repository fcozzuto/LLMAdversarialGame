def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if isinstance(resources, dict):
        resources = list(resources.items())
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    pursuer = (str(observation.get("self_role") or "")).lower().find("pursuer") >= 0
    away_from_op = pursuer  # heuristic: pursuer tries to get closer; otherwise try to avoid
    if not pursuer:
        away_from_op = True

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # resource attraction
        best_res = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2 and isinstance(r[0], (int, float)):
                rx, ry = int(r[0]), int(r[1])
                rv = float(r[2]) if len(r) >= 3 else 1.0
            elif isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                rv = 1.0
            else:
                continue
            d = cheb(nx, ny, rx, ry)
            if best_res is None or d < best_res[0]:
                best_res = (d, rv)
        res_bonus = 0.0
        if best_res is not None:
            d, rv = best_res
            res_bonus = rv * (20.0 / (1.0 + d))

        # opponent avoidance/approach
        d_op = cheb(nx, ny, ox, oy)
        op_term = (d_op if away_from_op else -d_op) * 2.0

        # slight center preference to reduce loops when tied
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = cheb(nx, ny, int(cx), int(cy)) * 0.1

        val = res_bonus + op_term - center_pen
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move