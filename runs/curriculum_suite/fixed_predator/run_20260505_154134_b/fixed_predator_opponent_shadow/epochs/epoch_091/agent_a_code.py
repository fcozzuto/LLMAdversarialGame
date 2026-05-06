def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose resource to contest: maximize (opponent farther - self farther), i.e., self is closer than opponent
    best_t = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        # Prefer strong leads; break ties toward nearer and toward low x/y for determinism
        key = (od - sd, -sd, -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (cx, cy)

    tx, ty = best_t

    # Evaluate candidate moves, penalize obstacle hits, and include slight repulsion from opponent to avoid being trapped
    best_move = [0, 0]
    best_val = None
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        hit_obst = (nx, ny) in obs
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Primary: increase contest advantage after moving; Secondary: reduce distance; Tertiary: avoid being adjacent to opponent
        opp_next_d = cheb(nx, ny, ox, oy)
        val = (nod - nsd, -nsd, opp_next_d, -abs(nx - tx) - abs(ny - ty))
        if hit_obst:
            val = (val[0] - 10, val[1] - 10, val[2] - 10, val[3] - 10)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move