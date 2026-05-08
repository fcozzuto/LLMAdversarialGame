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
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (d[0], d[1]))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_corner_far = cheb(nx, ny, far_corner[0], far_corner[1])
        d_corner_near = cheb(nx, ny, near_corner[0], near_corner[1])

        if is_evader:
            # Maximize distance from pursuer; also drift to the farthest corner.
            val = (d_opp * 1000) + (d_corner_far) - (d_corner_near // 2)
        else:
            # Pursue: minimize distance; also bias toward corner that is "near" to opponent's opposite.
            val = (-d_opp * 1000) + (d_corner_near // 2) - (d_corner_far // 2)

        if best is None or (val > best_val if is_evader else val > best_val):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]