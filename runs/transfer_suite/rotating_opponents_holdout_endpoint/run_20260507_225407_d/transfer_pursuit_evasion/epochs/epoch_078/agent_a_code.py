def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evad" in role) or ("escape" in role) or ("runner" in role)
    is_pursuer = not is_evader

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    # Deterministic move ordering (prefers diagonals)
    dirs = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        d_now = cheb(sx, sy, ox, oy)
        d_next = cheb(nx, ny, ox, oy)

        if is_pursuer:
            # Maximize capture pressure: minimize distance; break ties toward lower x then y
            score = -(d_next * 10) + (d_now - d_next)
        else:
            # Evader: maximize distance and drift toward farthest corner
            dc = cheb(nx, ny, far_corner[0], far_corner[1])
            score = (d_next * 10) + dc

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]