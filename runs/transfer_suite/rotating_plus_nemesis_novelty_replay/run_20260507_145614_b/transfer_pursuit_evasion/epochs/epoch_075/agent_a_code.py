def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    self_role = str(observation.get("self_role") or "pursuer").lower()
    is_evader = "evader" in self_role
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_res_d2(x, y):
        if not resources:
            return 0
        best = None
        for rx, ry in resources:
            d = dist2(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = dist2(nx, ny, ox, oy)
        d_res = nearest_res_d2(nx, ny)
        obst_pen = 0
        for bx, by in obst:
            dd = dist2(nx, ny, bx, by)
            if dd == 0:
                obst_pen = -999999
                break
            if dd < 2:
                obst_pen -= 3
        if is_evader:
            score = d_op * 10 - d_res + obst_pen
        else:
            score = -d_op * 10 - d_res + obst_pen
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]