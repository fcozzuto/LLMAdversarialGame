def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    second = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # primary: maximize opp's disadvantage; tie-break: smaller self distance, prefer higher "resource pressure"
        val = (do - ds, -ds, -(rx + ry))
        if best is None or val > best[0]:
            second = best
            best = (val, (rx, ry))
        elif second is None or val > second[0]:
            second = (val, (rx, ry))

    # If we are clearly behind best target, pivot to a safer alternative to reduce loss streak risk
    (_, (tx, ty)) = best
    if second is not None:
        ds_best = cheb(sx, sy, tx, ty)
        do_best = cheb(ox, oy, tx, ty)
        if do_best < ds_best and cheb(sx, sy, second[1][0], second[1][1]) <= ds_best + 1:
            tx, ty = second[1]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = (-10**18, 10**18, 10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_n = cheb(nx, ny, tx, ty)
        do_n = cheb(ox, oy, tx, ty)  # opponent doesn't move this step for our local greedy evaluation
        # Prefer moves that reduce our distance to target; if equal, prefer increasing opponent disadvantage; avoid stepping into obstacles already filtered
        cur_val = (-(ds_n), do_n - ds_n, abs(nx - ox) + abs(ny - oy))
        if cur_val > best_val:
            best_val = cur_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]