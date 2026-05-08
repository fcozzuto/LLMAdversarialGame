def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or ("chaser" in role)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def wall_score(x, y):
        lx = x if x < w - 1 - x else w - 1 - x
        ly = y if y < h - 1 - y else h - 1 - y
        return lx if lx < ly else ly

    def near_obstacle_penalty(x, y):
        p = 0
        for ax, ay in obstacles:
            dx = x - ax
            if dx < 0: dx = -dx
            dy = y - ay
            if dy < 0: dy = -dy
            d = dx if dx > dy else dy
            if d <= 1:
                p += 3 - d
        return p

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dxdy = (0, 0)
    if pursuer:
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            dist = cheb(nx, ny, ox, oy)
            both_axis = 1 if (nx != sx and ny != sy) else 0
            key = (dist, -both_axis, -(wall_score(nx, ny)), near_obstacle_penalty(nx, ny), nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_dxdy = (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]
    else:
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
                dx, dy = 0, 0
            dist = cheb(nx, ny, ox, oy)
            both_axis = 1 if (nx != sx and ny != sy) else 0
            key = (-dist, -both_axis, -(wall_score(nx, ny)), near_obstacle_penalty(nx, ny), nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_dxdy = (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]