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

    def count_adj_obstacles(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (0 <= nx < w and 0 <= ny < h) and ((nx, ny) in obstacles):
                c += 1
        return c

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            if inb(x + dx, y + dy):
                m += 1
        return m

    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if pursuer:
            # primary: get exact capture; then reduce distance; then prefer high mobility and avoid obstacle-sandwiches
            if nx == ox and ny == oy:
                val = (-10**9, 0, 0, 0)
            else:
                mob = mobility(nx, ny)
                adj_obs = count_adj_obstacles(nx, ny)
                val = (d, -mob, adj_obs, cheb(nx, ny, 0, 0) + cheb(nx, ny, w - 1, h - 1))
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]
        else:
            # evader: maximize distance; then high mobility; then minimize adjacency to obstacles
            if nx == ox and ny == oy:
                val = (10**9, 0, 0, 0)
            else:
                mob = mobility(nx, ny)
                adj_obs = count_adj_obstacles(nx, ny)
                val = (-d, -mob, adj_obs, cheb(nx, ny, 0, 0) - cheb(nx, ny, w - 1, h - 1))
            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best