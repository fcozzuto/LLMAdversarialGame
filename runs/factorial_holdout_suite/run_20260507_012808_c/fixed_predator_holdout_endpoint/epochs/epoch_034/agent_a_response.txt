def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def eval_pos(px, py):
        best_val = None
        best_sd = None
        for rx, ry in res:
            sd = dist_cheb(px, py, rx, ry)
            od = dist_cheb(ox, oy, rx, ry)
            val = (od - sd, -sd)  # maximize difference; then minimize self distance
            if best_val is None or val > best_val:
                best_val = val
                best_sd = sd
        if best_val is None:
            return (-10**9, 0, 0)
        # Small bonus for being closer to some resource, and far from opponent
        # to stabilize against oscillations.
        return (best_val[0], best_val[1], best_sd)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        sc = eval_pos(nx, ny)
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]