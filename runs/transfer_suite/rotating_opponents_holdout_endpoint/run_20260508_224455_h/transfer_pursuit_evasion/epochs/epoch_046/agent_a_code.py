def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    self_is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if self_is_evader:
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        edge_bias = 1
        best_val = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d_t = cheb(nx, ny, target[0], target[1])
            d_o = cheb(nx, ny, ox, oy)
            on_edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            val = (d_o, -d_t, edge_bias if on_edge else 0)
            if best_val is None or val > best_val:
                best_val, best_move = val, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        target = (ox, oy)
        edge_bias = -0.25
        best_val = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d_o = cheb(nx, ny, target[0], target[1])
            on_edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            val = (-d_o, edge_bias if on_edge else 0, -cheb(nx, ny, 0, 0))
            if best_val is None or val > best_val:
                best_val, best_move = val, (dx, dy)
        return [int(best_move[0]), int(best_move[1])]