def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_evader(nx, ny):
        d = cheb(nx, ny, ox, oy)
        corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
        fc = max(corners, key=lambda c: cheb(nx, ny, c[0], c[1]))
        dc = cheb(nx, ny, fc[0], fc[1])
        return (d, dc)

    def score_pursuer(nx, ny):
        d = cheb(nx, ny, ox, oy)
        corners = ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))
        fc = min(corners, key=lambda c: cheb(nx, ny, c[0], c[1]))
        dc = cheb(nx, ny, fc[0], fc[1])
        return (-d, dc)

    role = observation.get("self_role") or ""
    is_evader = "evader" in role.lower()

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        if is_evader:
            # Avoid stepping onto opponent (instant capture if capture_radius==0)
            if nx == ox and ny == oy:
                continue
            val = score_evader(nx, ny)
            if best is None or val > best:
                best = val
                best_move = (dx, dy)
        else:
            val = score_pursuer(nx, ny)
            if best is None or val > best:
                best = val
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]