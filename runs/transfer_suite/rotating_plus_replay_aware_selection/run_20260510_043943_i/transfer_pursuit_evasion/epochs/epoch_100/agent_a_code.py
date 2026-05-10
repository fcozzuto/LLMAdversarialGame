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
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1])) if is_evader else min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        corner_dist = cheb(nx, ny, corner[0], corner[1])
        step = cheb(sx, sy, nx, ny)
        # pursuer: minimize distance to opponent; evader: maximize distance
        if is_evader:
            score = dist * 1000 + corner_dist * 2 - step
        else:
            score = -dist * 1000 - corner_dist * 2 - step
        # deterministic tie-breaker: lexicographic on move
        if best is None or score > best or (score == best and [dx, dy] < best_move):
            best = score
            best_move = [dx, dy]

    # If all candidate moves invalid, stay
    return [int(best_move[0]), int(best_move[1])]