def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    resources_sorted = sorted(resources, key=lambda r: (r[0], r[1]))

    # Choose move by evaluating the best resource we could secure from the next position.
    # Primary: maximize our advantage (min opponent-self distance). Secondary: break ties by our distance to that resource.
    best_val = None
    best_move = [0, 0]
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        # For each resource, compute how favorable it is for us next turn+travel.
        # We use: opp_time - our_time; we want the minimum time disadvantage of the best target.
        best_target_adv = None
        best_target_dist = None
        for rx, ry in resources_sorted:
            my_t = cheb(nx, ny, rx, ry)
            op_t = cheb(ox, oy, rx, ry)
            adv = op_t - my_t  # positive means we're faster
            if best_target_adv is None or adv > best_target_adv or (adv == best_target_adv and my_t < best_target_dist):
                best_target_adv = adv
                best_target_dist = my_t

        # If we can't be faster to anything, still reduce the worst-case (most negative) opponent lead by selecting the target we maximize.
        val = (best_target_adv, -best_target_dist)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]