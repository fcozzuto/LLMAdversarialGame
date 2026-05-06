def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((a, b) for a, b in obstacles)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # Fallback: head toward our far corner while keeping away from opponent Chebyshev distance.
    if not resources:
        tx, ty = w - 1, h - 1
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny): 
                continue
            v = (cheb(nx, ny, ox, oy) * 100) - ((abs(nx - tx) + abs(ny - ty)) * 2)
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # Evaluate moves by how much better we are positioned for a future resource.
    best = [0, 0]; bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        # For this next position, choose best resource by opponent gap, then our speed, then center-aim.
        best_res_v = -10**18
        for rx, ry in resources:
            d_ours = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            gap = d_opp - d_ours  # positive means we are earlier
            # Encourage snapping to contested resources but avoid wandering:
            center_bias = -((abs(rx - (w/2)) + abs(ry - (h/2))) * 0.01)
            v = gap * 50 - d_ours * 2 + center_bias
            if v > best_res_v:
                best_res_v = v

        # Also lightly penalize moving too close to opponent to reduce denial clashes.
        v = best_res_v - cheb(nx, ny, ox, oy) * 0.2
        if v > bestv:
            bestv = v; best = [dx, dy]

    return best