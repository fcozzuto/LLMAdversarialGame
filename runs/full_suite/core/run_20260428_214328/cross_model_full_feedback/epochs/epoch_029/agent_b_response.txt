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

    # target nearest resource if available, else move to reduce distance to opponent
    best_move = None
    best_score = -10**9

    # prepare resource set
    res = [(int(p[0]), int(p[1])) for p in resources]

    for dx, dy, nx, ny in legal:
        score = 0
        # discourage stepping into opponent's square (handled by legal)
        # prefer moving toward a resource if any
        if res:
            dist_now = cheb(sx, sy, res[0][0], res[0][1])
            dist_next = cheb(nx, ny, res[0][0], res[0][1])
            if dist_next < dist_now:
                score += 5
        # avoid getting too close to opponent
        dist_to_opp = cheb(nx, ny, ox, oy)
        score -= dist_to_opp
        # small bias to move towards center diagonally if no resources
        if not res:
            if dx != 0 or dy != 0:
                score += 1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]