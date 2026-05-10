def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = observation.get("self_role", "pursuer")
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def nearest_corner_dist(x, y):
        best = 10**9
        for cx, cy in corners:
            d = cheb(x, y, cx, cy)
            if d < best:
                best = d
        return best

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    if role == "evader":
        best_score = -10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            corner_adv = -nearest_corner_dist(nx, ny)
            # add mild obstacle-avoidance: prefer cells with more free neighbors
            neigh = 0
            for ddx, ddy in candidates:
                tx, ty = nx + ddx, ny + ddy
                if free(tx, ty):
                    neigh += 1
            score = dist * 100 + corner_adv * 2 + neigh
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:  # pursuer
        best_cost = 10**18
        target_corner_dist = nearest_corner_dist(ox, oy)
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            # cornering if distances tie
            cornering = nearest_corner_dist(ox, oy) - nearest_corner_dist(nx, ny)
            # obstacle-avoidance: slightly penalize low mobility
            neigh = 0
            for ddx, ddy in candidates:
                tx, ty = nx + ddx, ny + ddy
                if free(tx, ty):
                    neigh += 1
            cost = dist * 1000 - cornering * 3 - neigh
            # tiny deterministic tie-break
            cost += (nx * 0.001 + ny * 0.0001)
            if cost < best_cost:
                best_cost = cost
                best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]