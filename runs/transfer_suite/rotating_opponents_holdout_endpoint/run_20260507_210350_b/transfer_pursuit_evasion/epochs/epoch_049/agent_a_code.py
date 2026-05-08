def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rolestr = (observation.get("self_role", "") or "").lower()
    is_evader = any(k in rolestr for k in ("evader", "escape", "flee", "runner"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        return dx if dx > dy else dy

    def edge_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def min_obs_dist(x, y):
        if not obstacles:
            return 10
        best = 10
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        ed = edge_dist(nx, ny)
        od = min_obs_dist(nx, ny)
        # Evader: maximize distance, stay away from obstacles and edges.
        # Pursuer: minimize distance; use edges/obstacles as soft tie-breakers.
        if is_evader:
            score = dist + 0.15 * ed + 0.25 * od
        else:
            score = -dist + 0.05 * ed + 0.05 * od
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]