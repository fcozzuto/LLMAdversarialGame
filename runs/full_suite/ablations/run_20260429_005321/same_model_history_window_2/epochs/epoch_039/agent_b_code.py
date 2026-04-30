def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer targets I'm closer to (d_me - d_op smaller), then shorter absolute distance.
            key = (d_me - d_op, d_me, abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

        rx, ry = best
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(nx, ny, ox, oy)  # tie-break: keep away from opponent
            # Also prefer moves that move generally toward the target (reduce distance to it).
            val = (d1, -d2, dx * (1 if rx > sx else (-1 if rx < sx else 0)) + dy * (1 if ry > sy else (-1 if ry < sy else 0)))
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move to maximize distance from opponent while staying valid.
    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if best_d is None or d > best_d:
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]