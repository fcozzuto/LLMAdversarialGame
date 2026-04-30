def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set((int(p[0]), int(p[1])) for p in obstacles)
    res = [(int(p[0]), int(p[1])) for p in resources]

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

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def dist_to_resource(nx, ny):
        if not res:
            return 0
        return min(cheb((nx, ny), r) for r in res)

    best = None
    best_score = None

    for dx, dy, nx, ny in legal:
        score = 0
        # Try to move toward nearest resource
        if res:
            d = dist_to_resource(nx, ny)
            score -= d * 2  # closer is better

        # Slight preference to proximity to opponent to pressure
        od = cheb((nx, ny), (ox, oy))
        score += od

        # Avoid getting too close to obstacle cluster if possible
        nearby_obst = 0
        for oxs, oys in obst:
            if max(abs(nx - oxs), abs(ny - oys)) <= 1:
                nearby_obst += 1
        score += nearby_obst * 0  # neutral but keeps structure

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy, nx, ny)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]