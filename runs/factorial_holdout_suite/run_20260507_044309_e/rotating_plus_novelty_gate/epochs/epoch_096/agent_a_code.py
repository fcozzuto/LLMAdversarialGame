def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    # Take adjacent resource immediately if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    # If no resources, move away from opponent while staying valid
    if not res_list:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            score = -cheb(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # Choose resource with best (our_dist_advantage over opponent): opp_dist - our_dist
    best_res = None
    best_adv = -10**9
    for rx, ry in res_list:
        adv = cheb(ox, oy, rx, ry) - cheb(sx, sy, rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)

    tx, ty = best_res

    # Greedy step toward target: minimize our distance, tie-break by higher advantage and then deterministic order
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_ours = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Advantage after move: opp_dist - our_dist (maximize)
        adv_after = d_opp - d_ours
        key = ( -d_ours, adv_after, -abs(nx - tx) - abs(ny - ty), dx, dy )
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]