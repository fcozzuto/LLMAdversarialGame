def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role) or ("runner" in str(observation.get("self_role","")).lower())

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1])) if is_evader else min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, best_corner[0], best_corner[1])

        if is_evader:
            score = (d_op * 100) + (d_corner) - (1 if (nx, ny) == (ox, oy) else 0)
            better = (best_score is None) or (score > best_score)
        else:
            score = (-d_op * 100) - (cheb(nx, ny, best_corner[0], best_corner[1]) * 2)
            better = (best_score is None) or (score > best_score)

        if better:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]