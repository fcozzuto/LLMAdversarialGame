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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def collide(x, y):
        return (x, y) in obst or (x, y) == (ox, oy)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and not collide(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        ax -= bx; ay -= by
        return max(abs(ax), abs(ay))

    resources_pos = [(int(p[0]), int(p[1])) for p in resources]
    best_move = None
    best_score = -10**9

    for dx, dy, nx, ny in legal:
        score = 0
        if (nx, ny) == (ox, oy):
            score -= 1000
        dist_to_opp = cheb((nx, ny), (ox, oy))
        score -= dist_to_opp

        if resources_pos:
            # prefer moving toward nearest resource while not stepping into opponent
            nearest_res = min(resources_pos, key=lambda r: cheb((nx, ny), r))
            dist_res = cheb((nx, ny), nearest_res)
            score -= dist_res

        # slight bias to move towards center to reduce edge trapping
        center_dx = abs(nx - w//2)
        center_dy = abs(ny - h//2)
        score -= (center_dx + center_dy) // 2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]