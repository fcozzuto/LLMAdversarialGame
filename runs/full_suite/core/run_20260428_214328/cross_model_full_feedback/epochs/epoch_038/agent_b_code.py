def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a_x, a_y, b_x, b_y):
        dx = abs(a_x - b_x)
        dy = abs(a_y - b_y)
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist_to_resource(nx, ny):
        if not res:
            return 0
        return min(cheb(nx, ny, rx, ry) for rx, ry in res)

    best = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        ds = dist_to_resource(nx, ny)
        # Prefer positions closer to resources and further from opponent
        dob = cheb(nx, ny, ox, oy)
        score = (ds * -2) + (dob * 0.5)
        if best is None or score < best:
            best = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]