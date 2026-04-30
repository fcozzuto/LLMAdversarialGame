def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obs_set = set((a, b) for a, b in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # If no resources, just move toward opponent farthest? Keep safe: maximize distance from opponent.
    if not resources:
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obs_set:
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[1]:
                best = ((dx, dy), d)
        return best[0] if best[0] is not None else [0, 0]

    # Choose a resource where opponent is relatively farther: (opp_dist - self_dist) then self_dist.
    best_res = None
    best_val = -10**18
    best_sdist = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = od - sd
        if val > best_val or (val == best_val and sd < best_sdist):
            best_val = val
            best_sdist = sd
            best_res = (rx, ry)
    rx, ry = best_res

    # Evaluate candidate moves toward target while avoiding close proximity to opponent and obstacles.
    curr_do = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        dt = cheb(nx, ny, rx, ry)
        do = cheb(nx, ny, ox, oy)
        # Encourage progress; discourage getting too close to opponent; small bias against moving away from target.
        score = (-dt * 10)
        if do <= 1:
            score -= 30
        elif do == 2:
            score -= 12
        elif do == 3:
            score -= 4
        # Prefer improving relative to current distance to opponent (be safer if losing).
        if do < curr_do:
            score -= (curr_do - do) * 6
        else:
            score += 2
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]