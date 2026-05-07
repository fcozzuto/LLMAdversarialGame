def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Pick target resource where we have the largest (opp_time - self_time).
    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, -rx, -ry)  # maximize advantage, then faster, then deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    # From legal moves, choose the one that improves our advantage toward the target.
    best_move = (0, 0, sx, sy)
    best_move_key = None
    for dx, dy, nx, ny in legal:
        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)
        adv = od2 - sd2
        move_key = (adv, -sd2, dx, dy, nx, ny)  # deterministic
        if best_move_key is None or move_key > best_move_key:
            best_move_key = move_key
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]