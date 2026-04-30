def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    dxs = (-1, 0, 1)
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def nearest_resource_dist(x, y):
        if not resources: 
            return 10**9
        best = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d < best: best = d
        return best
    best_move = [0, 0]
    best_val = -10**18
    self_to_op = cheb(sx, sy, ox, oy)
    opp_to_res = nearest_resource_dist(ox, oy)
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d_self_res = nearest_resource_dist(nx, ny)
            on_resource = 1 if any(nx == rx and ny == ry for rx, ry in resources) else 0
            d_opp = cheb(nx, ny, ox, oy)
            d_opp_near_after = opp_to_res
            if resources:
                # approximate opponent progress by how far they could be from the same nearest resource after our move
                pass
            val = 0
            val += on_resource * 1000
            val += -3.5 * d_self_res
            val += 0.6 * d_opp
            # slight preference to also move away from opponent when they are close
            if self_to_op <= 2:
                val += 1.2 * d_self_res * 0.0
                val += 0.8 * d_opp
            # if opponent already closer to remaining resources, prioritize pushing towards them
            if nearest_resource_dist(sx, sy) > opp_to_res:
                val += 1.0 * (opp_to_res - d_self_res)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    return best_move