def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))
    opp_is_pursuer = any(k in role_opp for k in ("pursuer", "chaser", "hunter"))
    pursuer_mode = self_is_pursuer if (self_is_pursuer or opp_is_pursuer) else True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_move(nx, ny):
        d = cheb(nx, ny, ox, oy)
        # Center/edge bias to help cornering or escape deterministically
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - cx) + abs(ny - cy)

        # Obstacle penalty to avoid hugging blocked cells (not strictly needed but deterministic)
        adj_block = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                adj_block += 1

        if pursuer_mode:
            # Minimize distance; slight preference to reduce center_dist and reduce adjacent blocks
            return (d, center_dist, adj_block)
        else:
            # Maximize distance; slight preference to increase center_dist (avoid center) and reduce adj blocks
            return (-d, -center_dist, adj_block)

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        s = score_move(nx, ny)
        if best is None or s < best:
            best, best_move = s, [dx, dy]

    # If all candidate moves are blocked/out of bounds, stay put
    return best_move