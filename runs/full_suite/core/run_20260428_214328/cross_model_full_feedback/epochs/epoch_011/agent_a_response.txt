def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    resources = set((p[0], p[1]) for p in resources_list)
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) != (ox, oy)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    remaining = observation.get("remaining_resource_count", 0)
    tight = 2 if remaining <= 4 else 1  # more aggressive when few resources remain

    best = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        my_best = None
        for rx, ry in resources:
            if not inside(rx, ry) or (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # prefer landing on resource, then resources closer to us than opponent
            v = 0
            if (nx, ny) == (rx, ry):
                v += 100000
            v += (do - ds) * 1000
            # slight preference to get closer overall (reduces pathing ambiguity)
            v += (do - ds) * (-tight)
            v += (-(ds))  # lower ds better
            if my_best is None or v > my_best:
                my_best = v
        # If no resources exist, just head toward opponent's resources area: minimize own to nearest edge
        if my_best is None:
            my_best = -(cheb(nx, ny, 0, 0) + cheb(nx, ny, w-1, h-1))
        # tie-break: deterministic order by preferring diagonal/forward-ish movement toward opponent vicinity
        if best_val is None or my_best > best_val:
            best_val = my_best
            best = (dx, dy)
        elif my_best == best_val:
            # prefer moves that reduce distance to opponent (potentially contest later)
            cur_do = cheb(nx, ny, ox, oy)
            best_dx, best_dy = best
            bx, by = sx + best_dx, sy + best_dy
            best_do = cheb(bx, by, ox, oy)
            if cur_do < best_do:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]