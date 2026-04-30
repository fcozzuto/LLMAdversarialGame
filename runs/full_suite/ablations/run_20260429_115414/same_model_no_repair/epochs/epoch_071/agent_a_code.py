def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def min_obst_dist(x, y):
        if not obstacles:
            return 99
        best = 10**9
        for px, py in obstacles:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        return best

    # Pick resource that maximizes our relative closeness (opp_dist - self_dist)
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)
    if best_t is None:
        best_t = (w // 2, h // 2)
    tx, ty = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Prefer getting closer relative to opponent, avoid obstacles, and grab resources immediately
        val = (opp_d - self_d)
        if resources:
            if (nx, ny) in set(map(tuple, resources)):
                val += 6
            else:
                # Mild preference for reducing distance to nearest resource
                nd = 10**9
                for rx, ry in resources:
                    d = cheb(nx, ny, rx, ry)
                    if d < nd:
                        nd = d
                val -= 0.08 * nd
        md = min_obst_dist(nx, ny)
        val -= 1.2 / (1 + md)
        # Tie-break deterministically toward smaller cheb to target
        if val > best_val or (val == best_val and self_d < cheb(sx + best_move[0], sy + best_move[1], tx, ty)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]