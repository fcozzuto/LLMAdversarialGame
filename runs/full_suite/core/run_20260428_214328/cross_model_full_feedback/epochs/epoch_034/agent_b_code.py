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

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def collides(nx, ny): return (nx, ny) in obst or (nx, ny) == (ox, oy)
    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and not collides(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Heuristic: prefer moving toward nearest resource, then away from opponent if possible
    def dist_to_nearest_resource(nx, ny):
        if not res:
            return 0
        return min(cheb(nx, ny, rx, ry) for rx, ry in res)

    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        score = 0
        if res:
            d_res = dist_to_nearest_resource(nx, ny)
            score -= d_res * 2  # prefer closer to resources
        # penalize closeness to opponent to avoid capture
        opp_dist = cheb(nx, ny, ox, oy)
        score -= max(0, 2 - opp_dist) * 3  # discourage approaching if close
        # small bias to keep moving if equal
        score += 0
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy, nx, ny)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]