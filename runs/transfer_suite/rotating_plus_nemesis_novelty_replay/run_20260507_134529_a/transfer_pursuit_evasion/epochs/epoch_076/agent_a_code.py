def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy)) if not is_evader else min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    tcx, tcy = target_corner

    best_move = [0, 0]
    best_val = None

    for dx, dy in sorted(moves, key=lambda d: (d[0], d[1])):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, tcx, tcy)
        if is_evader:
            val = -(1.5 * d_opp + 0.5 * d_corner)
        else:
            val = (1.2 * d_opp + 0.8 * d_corner)
        if best_val is None or (val < best_val if not is_evader else val < best_val):
            best_val = val
            best_move = [dx, dy]

    if not ok(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return best_move