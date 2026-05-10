def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def sqd(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("evade" in role) or ("runner" in role) or ("escape" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if cheb(sx, sy, ox, oy) <= 2 and is_evader:
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    elif is_evader:
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        target = (ox, oy)

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_t = cheb(nx, ny, target[0], target[1])
        if is_evader:
            val = (d_opp * 1000 + d_t)  # primary: maximize separation
            if best_val is None or val > best_val:
                best_val, best = val, (dx, dy)
        else:
            val = (-d_t * 1000 - d_opp)  # primary: minimize distance to opponent (via target)
            if best_val is None or val > best_val:
                best_val, best = val, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]