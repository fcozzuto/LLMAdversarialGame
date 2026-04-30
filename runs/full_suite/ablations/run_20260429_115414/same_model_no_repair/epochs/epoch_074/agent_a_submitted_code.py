def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

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

    def passable(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def near_obst_pen(x, y):
        if not obstacles:
            return 0
        best = 10**9
        for px, py in obstacles:
            d = cheb(x, y, px, py)
            if d < best:
                best = d
        if best <= 0:
            return 100
        if best == 1:
            return 6
        if best == 2:
            return 2
        return 0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose target resource by maximizing our distance advantage (opp - us).
    if resources:
        best_t = None
        best_adv = -10**9
        best_d = 10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and ds < best_d):
                best_adv = adv
                best_d = ds
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # If no resources visible, drift to center while staying safe.
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_val = -10**18
    # Move evaluation: maximize (opp_dist_to_target - our_dist_after) while avoiding obstacles.
    # If tied, prefer moves that reduce our distance to target, then keep closer to center.
    cx, cy = w // 2, h // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        val = (opp_d - our_d) - near_obst_pen(nx, ny)
        # Tie-breakers: higher val first, then smaller our_d, then smaller center distance, then deterministic move order.
        center_d = cheb(nx, ny, cx, cy)
        if val > best_val or (val == best_val and (our_d < cheb(best_move[0] + sx, best_move[1] + sy, tx, ty)
                                                  or (our_d == cheb(best_move[0] + sx, best_move[1] + sy, tx, ty) and
                                                      center_d < cheb(best_move[0] + sx, best_move[1] + sy, cx, cy))))):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[