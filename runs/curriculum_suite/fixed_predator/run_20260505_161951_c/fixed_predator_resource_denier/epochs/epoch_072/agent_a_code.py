def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Denial: resources currently closer to opponent than us
    base_denies = []
    for rx, ry in resources:
        d_self0 = cheb(x, y, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        if d_opp + 1 < d_self0:
            base_denies.append((d_self0, rx, ry))
    denial_target = min(base_denies)[1:] if base_denies else None

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Our "capture advantage"
        best_margin = -10**18
        best_dist = 10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            margin = d_opp - d_self
            if margin > best_margin or (margin == best_margin and d_self < best_dist):
                best_margin = margin
                best_dist = d_self

        # Denial pressure: if opponent is ahead somewhere, reduce our distance to it
        denial_term = 0
        if denial_target is not None:
            tx, ty = denial_target
            denial_term = -cheb(nx, ny, tx, ty)

        # Minor opponent-distance shaping to avoid getting trapped while marching
        opp_shape = -cheb(nx, ny, ox, oy)

        val = best_margin * 1000 - best_dist * 3 + denial_term * 8 + opp_shape * 0.3
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move