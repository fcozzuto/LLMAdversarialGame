def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    tx, ty = ox, oy
    if is_evader:
        best = None
        best_d2 = -1
        for cx, cy in corners:
            d2 = dist2(cx, cy, ox, oy)
            if d2 > best_d2:
                best_d2 = d2
                best = (cx, cy)
        tx, ty = best

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d2_op = dist2(nx, ny, ox, oy)
        d2_goal = dist2(nx, ny, tx, ty)
        penalty = 0
        if (nx, ny) in obst:
            penalty = 10**9
        if is_evader:
            val = d2_op - 0.05 * d2_goal + penalty
            better = (best_val is None) or (val > best_val)
        else:
            val = -d2_op - 0.01 * d2_goal - penalty
            better = (best_val is None) or (val > best_val)
        if better:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]