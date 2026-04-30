def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = set((x, y) for x, y in obstacles)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        return [0, 0]

    best_r = resources[0]
    best_adv = None
    best_dist = None
    for r in resources:
        rx, ry = r
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        adv = d_opp - d_self
        if best_adv is None or adv > best_adv or (adv == best_adv and d_self < best_dist):
            best_adv = adv
            best_dist = d_self
            best_r = r
    tx, ty = best_r

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        dist_to_target = cheb(nx, ny, tx, ty)
        dist_to_opp = cheb(nx, ny, ox, oy)
        # Prefer closer to target; when tied, prefer to be farther from opponent.
        key = (dist_to_target, -dist_to_opp, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]