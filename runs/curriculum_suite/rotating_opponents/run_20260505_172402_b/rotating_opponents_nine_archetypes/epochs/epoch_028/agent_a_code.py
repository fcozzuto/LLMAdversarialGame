def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18

    # Pick a resource to compete over: maximize our advantage (opp_d - self_d), tie-break closer to it.
    best_r = None
    best_r_adv = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_r_adv or (adv == best_r_adv and (sd < (cheb(sx, sy, int(best_r[0]), int(best_r[1]))) if best_r else True)):
            best_r_adv = adv
            best_r = (rx, ry)

    rx, ry = best_r

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        my_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)

        # Greedy race advantage + mild opponent distance shaping + obstacle-aware move preference.
        # Encourage moves that reduce our distance to the resource while increasing opponent's distance to our current region.
        opp_to_new = cheb(ox, oy, nx, ny)
        near_obs = 0
        for (ox2, oy2) in obs:
            d = cheb(nx, ny, ox2, oy2)
            if d == 0:
                near_obs -= 5
            elif d == 1:
                near_obs -= 1
            elif d == 2:
                near_obs -= 0.25

        # Core: maximize (opp_d - my_d), meaning we stay/approach sooner than opponent.
        val = (opp_d - my_d) * 10.0 + (opp_to_new) * 0.15 - my_d * 0.05 + near_obs
        # Tie-break deterministically: prefer moves that keep dx,dy smaller lexicographically.
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move