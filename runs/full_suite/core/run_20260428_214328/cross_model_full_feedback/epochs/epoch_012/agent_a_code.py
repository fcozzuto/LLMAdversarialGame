def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = observation.get("obstacles", None) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", None) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obs

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        if res:
            d = min(dist((nx, ny), r) for r in res)
        else:
            d = 0
        # Prefer approaching resources; if none, prefer moving away from opponent
        opp = dist((nx, ny), (ox, oy))
        score = (d, -opp) if res else (-opp, 0)
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]
    if best is not None:
        return best

    # Fallback: any valid non-blocked move, deterministic
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny) and (nx, ny) != (ox, oy):
            return [dx, dy]
    return [0, 0]