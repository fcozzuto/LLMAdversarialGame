def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_pos(px, py):
        if not resources:
            tx, ty = w - 1, h - 1
            return cheb(px, py, ox, oy) * 5 - (abs(px - tx) + abs(py - ty))
        best = -10**18
        for rx, ry in resources:
            d_s = cheb(px, py, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            adv = d_o - d_s  # positive => we can reach first (or tie-break by being closer)
            # also consider their advantage if we move elsewhere
            take_val = adv * 120 - d_s
            deny_val = (-adv) * 60 - d_s * 0.5
            # if opponent already much closer, prioritize denying it
            cur_opp_adv = d_o - cheb(x, y, rx, ry)
            if cur_opp_adv > 0:
                cur = deny_val + cur_opp_adv * 40
            else:
                cur = take_val
            if cur > best:
                best = cur
        # slight pressure to not hand them proximity
        best -= cheb(px, py, ox, oy) * 0.1
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        v = eval_pos(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]