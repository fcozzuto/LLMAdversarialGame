def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    # If we can grab a resource immediately, do it.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    # Choose the resource that gives us the biggest lead (dist_opp - dist_self).
    best_res = None; best_lead = -10**9
    for rx, ry in res_list:
        lead = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
        if lead > best_lead:
            best_lead = lead; best_res = (rx, ry)

    # If none, head deterministically toward the center.
    if best_res is None:
        tx, ty = w // 2, h // 2
        best_move = [0, 0]; best_d = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_d:
                best_d = d; best_move = [dx, dy]
        return best_move

    rx, ry = best_res
    # Move to reduce our distance to the chosen resource, but if we can't, at least don't worsen lead much.
    best_move = [0, 0]; best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        lead = d_opp - d_self
        d_res_now = cheb(sx, sy, rx, ry)
        improve = d_res_now - d_self  # positive is improvement
        # Key: maximize lead, then maximize immediate improvement, then deterministic tie-break by direction order.
        key = (lead, improve, -abs(nx - rx) - abs(ny - ry))
        if best_key is None or key > best_key:
            best_key = key; best_move = [dx, dy]
    return best_move