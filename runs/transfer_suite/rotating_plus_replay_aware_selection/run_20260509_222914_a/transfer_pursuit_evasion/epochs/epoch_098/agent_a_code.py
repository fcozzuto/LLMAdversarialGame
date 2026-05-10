def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = any(k in role for k in ("evader", "runner", "escape", "fugitive"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_obst_dist(x, y):
        if not obstacles:
            return 10**6
        best = 10**9
        for bx, by in obstacles:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    best_mv = (0, 0)
    best_sc = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_op = man(nx, ny, ox, oy)
        d_ob = best_obst_dist(nx, ny)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        d_corner = max(man(nx, ny, cx, cy) for cx, cy in corners)
        sc = 0
        if is_evader:
            sc = 10 * d_op + 2 * d_corner + d_ob
        else:
            sc = 10 * (-d_op) + 2 * d_ob + 0.5 * (-d_corner)
        if sc > best_sc or (sc == best_sc and (dx, dy) < best_mv):
            best_sc = sc
            best_mv = (dx, dy)

    dx, dy = best_mv
    return [int(dx), int(dy)]