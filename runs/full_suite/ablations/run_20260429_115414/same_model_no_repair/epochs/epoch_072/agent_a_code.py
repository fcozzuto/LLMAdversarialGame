def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

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

    def min_obst_dist(x, y):
        if not obstacles:
            return 99
        best = 10**9
        for px, py in obstacles:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        return best

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        # If no resources, drift toward center while avoiding obstacles
        tx, ty = w // 2, h // 2
    else:
        best_t = None
        best_adv = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv:
                best_adv = adv
                best_t = (rx, ry)
        tx, ty = best_t

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if not passable(nx, ny):
            continue

        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        adv = d_opp - d_self  # higher is better: we are closer than opponent

        # Obstacle safety: strongly avoid being adjacent/at-risk
        md = min_obst_dist(nx, ny)
        safety = md
        # Small preference to keep moving when tied
        move_eff = -((dx == 0 and dy == 0) * 0.5)

        # Prefer positions that don't lag too far behind best advancement
        score = adv * 10 - d_self + safety * 2 + move_eff
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move == (0, 0) and not passable(sx, sy):
        # Shouldn't happen, but keep deterministic fallback
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]