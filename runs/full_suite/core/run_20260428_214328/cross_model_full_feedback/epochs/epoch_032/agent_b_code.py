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

    res = [(int(p[0]), int(p[1])) for p in resources]

    # If no resources, move toward center while avoiding opponent
    if not res:
        best = None
        bestd = 10**9
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, w//2, h//2)
            if d < bestd:
                bestd = d; best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0,0]

    # Evaluate moves by a simple heuristic:
    # prioritize getting closer to nearest resource, then reduce proximity to opponent,
    # and avoid stepping into obstacle.
    def nearest_resource_dist(px, py):
        best = 10**9
        for tx, ty in res:
            d = cheb(px, py, tx, ty)
            if d < best: best = d
        return best

    best_move = None
    best_score = -10**9
    opp_near_penalty = 5

    for dx, dy, nx, ny in legal:
        score = 0
        # closeness to nearest resource
        nr = nearest_resource_dist(nx, ny)
        score -= nr * 2  # incentivize approaching resource

        # penalize being close to opponent to avoid collision risk
        oppdist = cheb(nx, ny, ox, oy)
        score -= max(0, (3 - oppdist)) * opp_near_penalty

        # slight bonus if moving directly toward resource
        if res:
            closest = min(res, key=lambda t: cheb(nx, ny, t[0], t[1]))
            if cheb(nx, ny, closest[0], closest[1]) == 1:
                score += 2

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]