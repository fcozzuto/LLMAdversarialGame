def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    neigh8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    def best_target_dist(x, y):
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if best is None or d < best:
                best = d
        return best

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        pen = obst_adj_pen(nx, ny)
        if resources:
            dist = best_target_dist(nx, ny)
            val = -dist - 0.2 * pen
            if observation.get("remaining_resource_count") == 0:
                val = -dist - 0.2 * pen
        else:
            dist_op = cheb(nx, ny, ox, oy)
            val = dist_op - 0.2 * pen  # deterministic fallback
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        dx, dy = 0, 0
    return [int(dx), int(dy)]