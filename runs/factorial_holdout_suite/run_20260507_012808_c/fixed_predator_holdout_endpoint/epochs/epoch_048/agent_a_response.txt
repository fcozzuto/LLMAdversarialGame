def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    # Prefer moves that (1) reduce our distance to some resource, (2) keep opponent far, (3) avoid walls by staying closer to center.
    best_move = (0, 0)
    best_key = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Choose the target resource that maximizes immediate advantage for this candidate move.
        local_best = None
        for rx, ry in resources:
            self_d = dist_cheb(nx, ny, rx, ry)
            opp_d = dist_cheb(ox, oy, rx, ry)
            # If we can capture immediately, heavily prefer.
            capture = 1000 if self_d == 0 else 0
            # Tie-break: smaller self distance; larger advantage.
            key = (capture + (opp_d - self_d), -self_d)
            if local_best is None or key > local_best:
                local_best = key
        # Center bias (small) and slight penalty for moving too much to keep stable.
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.0001
        move_key = (local_best[0], local_best[1], center_bias, -abs(dx) - abs(dy))
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]