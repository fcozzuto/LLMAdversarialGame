def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not resources:
        return [0, 0]

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

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if isinstance(rx, int) and isinstance(ry, int) and not blocked(rx, ry):
                res_list.append((rx, ry))
    if not res_list:
        return [0, 0]

    def best_utility(px, py):
        best_u = -10**18
        best_du = 10**9
        for rx, ry in res_list:
            du = cheb(px, py, rx, ry)
            dov = cheb(ox, oy, rx, ry)
            u = (dov - du) * 100 - du
            if u > best_u or (u == best_u and du < best_du):
                best_u = u
                best_du = du
        return best_u, best_du

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cur_u, cur_du = best_utility(sx, sy)

    best_move = (0, 0)
    best_u = cur_u
    best_du = cur_du

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        u, du = best_utility(nx, ny)
        if u > best_u or (u == best_u and du < best_du):
            best_u, best_du = u, du
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]