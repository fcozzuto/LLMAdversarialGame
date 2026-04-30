def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    sx = int(sx); sy = int(sy)
    ox = int(ox); oy = int(oy)

    obst = set((int(p[0]), int(p[1])) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def collides(nx, ny):
        return (nx, ny) in obst or (nx, ny) == (ox, oy)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and not collides(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Prefer moving toward closest resource; as tie-breaker, move toward opponent
    best_move = None
    best_score = -10**9

    res = [(int(p[0]), int(p[1])) for p in resources]

    for dx, dy, nx, ny in legal:
        score = 0
        # distance to opponent (we want to control space)
        dist_opp = cheb(nx, ny, ox, oy)
        score -= dist_opp * 2

        if res:
            # distance to nearest resource
            d_res = 10**9
            for rx, ry in res:
                d = cheb(nx, ny, rx, ry)
                if d < d_res:
                    d_res = d
            score -= d_res

        # prefer staying closer to center for stability
        center_dx = abs(nx - w//2)
        center_dy = abs(ny - h//2)
        score -= max(center_dx, center_dy) * 0.1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]