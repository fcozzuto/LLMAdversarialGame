def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)
    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    rs = [(int(p[0]), int(p[1])) for p in resources]

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

    def dist_cheb(a, b):
        ax, ay = a; bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    # Prefer moving toward nearest resource while keeping safe distance from opponent
    best_move = None
    best_score = -10**9

    for dx, dy, nx, ny in legal:
        score = 0
        # Avoid bumping into opponent
        if (nx, ny) == (ox, oy):
            score -= 1000
        # Distance to opponent heuristic
        score -= max(abs(nx - ox), abs(ny - oy))
        # Resource proximity
        if rs:
            dmin = min(dist_cheb((nx, ny), r) for r in rs)
            score += max(0, 8 - dmin)
        # Centeredness (favor staying toward center to reduce edge traps)
        score -= max(abs(nx - (w-1)/2), abs(ny - (h-1)/2)) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]