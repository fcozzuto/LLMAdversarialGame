def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set(obstacles)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

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

    def best_resource_score(nx, ny):
        if not resources:
            return 0, 10**9, None
        best_adv = -10**18
        best_d = 10**18
        best_r = None
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            adv = op_d - my_d
            if (adv > best_adv) or (adv == best_adv and my_d < best_d):
                best_adv = adv
                best_d = my_d
                best_r = (rx, ry)
        return best_adv, best_d, best_r

    best_move = (0, 0)
    best_val = -10**18
    best_tieb = (10**18, 10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        adv, my_d, _ = best_resource_score(nx, ny)
        op_d = cheb(ox, oy, nx, ny)
        # Strongly avoid giving the opponent immediate adjacency advantage
        val = adv * 1000 - op_d
        tieb = (my_d, abs(nx - ox) + abs(ny - oy))
        if val > best_val or (val == best_val and tieb < best_tieb):
            best_val = val
            best_tieb = tieb
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]