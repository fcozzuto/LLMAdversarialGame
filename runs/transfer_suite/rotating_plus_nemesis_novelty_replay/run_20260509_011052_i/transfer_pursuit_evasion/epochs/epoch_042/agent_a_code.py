def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def nearest_resource_dist(x, y):
        if not resources:
            return None
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18

    target_is_resource = bool(resources) and int(observation.get("remaining_resource_count", len(resources)) or len(resources)) > 0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if target_is_resource:
            d = nearest_resource_dist(nx, ny)
            score = -d
            if resources:
                for rx, ry in resources:
                    if nx == rx and ny == ry:
                        score += 1000
                        break
        else:
            d = cheb(nx, ny, ox, oy)
            score = -d + (-cheb(nx, ny, sx, sy) * 0.01)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]