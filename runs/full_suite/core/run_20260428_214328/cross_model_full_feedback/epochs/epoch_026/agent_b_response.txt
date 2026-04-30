def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles_list = observation.get("obstacles", []) or []
    resources_list = observation.get("resources", []) or []
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)
    obst = set((int(p[0]), int(p[1])) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def collide(nx, ny):
        return (nx, ny) in obst or (nx, ny) == (ox, oy)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and not collide(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    rs = [(int(p[0]), int(p[1])) for p in resources_list]

    def dist_cheb(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    best_move = None
    best_score = -10**9

    for dx, dy, nx, ny in legal:
        score = 0
        if (nx, ny) == (ox, oy):
            score -= 1000
        if rs:
            dmin = min(dist_cheb((nx, ny), r) for r in rs)
            score += max(0, 8 - dmin)
        score -= max(abs(nx - ox), abs(ny - oy))  # discourage staying near opponent
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]