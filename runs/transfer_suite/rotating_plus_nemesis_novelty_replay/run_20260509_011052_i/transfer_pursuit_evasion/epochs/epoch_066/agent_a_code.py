def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            if inb(x + dx, y + dy):
                m += 1
        return m

    def nearest_obstacle_dist(x, y):
        best = 10**9
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d < best:
                best = d
        return best if obstacles else 99

    best = None
    best_val = -10**18 if pursuer else 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if pursuer:
            val = -d * 10.0
            if nx == ox and ny == oy:
                val = 1e9
            val += mobility(nx, ny) * 0.35
            val += (nearest_obstacle_dist(nx, ny) - 1) * 0.08
            val += -((0 if dx == 0 else 1) + (0 if dy == 0 else 1)) * 0.01  # slight prefer straighter
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), val
        else:
            # evader: maximize distance, prefer staying mobile and away from obstacles
            val = d * 10.0
            val += mobility(nx, ny) * 0.35
            val += (nearest_obstacle_dist(nx, ny) - 1) * 0.12
            if best is None or val > best_val or (val == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]