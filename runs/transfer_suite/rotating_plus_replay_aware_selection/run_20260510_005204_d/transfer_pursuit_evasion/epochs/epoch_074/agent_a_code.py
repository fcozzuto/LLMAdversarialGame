def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if we_evader:
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    def move_score(nx, ny):
        if (nx, ny) in blocked:
            return -10**9
        s = 0
        dist_to_target = cheb(nx, ny, tx, ty)
        if we_evader:
            s += 40 - 3 * dist_to_target
            s -= 2 * cheb(nx, ny, ox, oy)
        else:
            s += 40 - 3 * dist_to_target
            s += 2 * (8 - cheb(nx, ny, ox, oy))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (nx + dx, ny + dy) in blocked:
                    s -= 2 if (dx != 0 or dy != 0) else 25
        return s

    best = None
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        sc = move_score(nx, ny)
        if sc > best_s or (sc == best_s and (dx, dy) < (best[0], best[1]) if best else True):
            best_s = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]