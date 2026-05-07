def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    env = observation.get("environment_name", "resource_collection")
    if env != "resource_collection":
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    best_du = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
        max_u = -10**18
        min_du_here = 10**9
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not (isinstance(rx, int) and isinstance(ry, int)):
                continue
            if blocked(rx, ry):
                continue
            du = cheb(nx, ny, rx, ry)
            dov = cheb(ox, oy, rx, ry)
            u = (dov - du) * 10 - du
            if u > max_u:
                max_u = u
            if du < min_du_here:
                min_du_here = du
        # tie-break: prefer smaller our distance and then deterministic move order
        if max_u > best_val or (max_u == best_val and (min_du_here < best_du)):
            best_val = max_u
            best_du = min_du_here
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]