def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    res_list = [tuple(r) for r in resources]
    res_set = set(res_list)

    # Immediate collection
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set:
            return [dx, dy]

    # If no resources exist, just reduce distance to opponent safely
    if not res_list:
        best = None; bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best if best is not None else [0, 0]

    # Advantage heuristic: maximize (opp_closest_dist - self_closest_dist),
    # tie-breaker: prefer moves that move toward own closest resource.
    def min_dist_to_resources(x, y):
        md = 10**9
        for rx, ry in res_list:
            d = cheb(x, y, rx, ry)
            if d < md:
                md = d
        return md

    s_md = min_dist_to_resources(sx, sy)
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_md = min_dist_to_resources(nx, ny)
        opp_md = min_dist_to_resources(ox, oy)
        v = (opp_md - self_md)
        # Tie-break: reduce own distance, then reduce distance to opponent (deterministic)
        v2 = (s_md - self_md)
        v3 = -cheb(nx, ny, ox, oy)
        score = (v * 1000000) + (v2 * 1000) + v3
        if score > bestv:
            bestv = score; best = [dx, dy]
    return best