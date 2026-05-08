def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))

    def choose_target():
        if not res:
            # Head toward the middle band away from opponent to meet future resources
            tx = (w - 1) // 2
            ty = (h - 1) // 2
            if ox > sx:
                tx = max(0, tx - 1)
            if oy > sy:
                ty = max(0, ty - 1)
            return (tx, ty)
        best = None
        bestv = -10**9
        for (x, y) in res:
            ds = cheb(x, y, sx, sy)
            do = cheb(x, y, ox, oy)
            # Prefer ones we can reach not later than opponent, and break ties toward closer
            lead = do - ds
            v = 3.0 * lead - 0.15 * ds - 0.01 * (abs(x - (w-1)/2) + abs(y - (h-1)/2))
            if v > bestv:
                bestv = v
                best = (x, y)
        return best

    tx, ty = choose_target()
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Greedy toward target, but keep pressure if opponent is closer to that target
        v = -cheb(nx, ny, tx, ty) + 0.9 * (cheb(ox, oy, tx, ty) - cheb(nx, ny, ox, oy))
        # Small bias to reduce oscillation: favor moves that don't increase distance to target too much
        v -= 0.02 * cheb(nx, ny, sx, sy)
        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]