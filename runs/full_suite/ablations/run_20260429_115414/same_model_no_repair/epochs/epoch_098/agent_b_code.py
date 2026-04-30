def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource where we have the best distance advantage over opponent.
    best_r = resources[0]
    best_adv = -10**18
    best_sd = 10**18
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_sd):
            best_adv = adv
            best_sd = sd
            best_r = (rx, ry)

    tx, ty = best_r

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = 10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        # Heuristic: move closer to target while avoiding being adjacent to obstacles.
        d_to_t = cheb(nx, ny, tx, ty)
        obs_adj = 0
        for ax, ay in obstacles:
            dd = cheb(nx, ny, ax, ay)
            if dd == 0:
                obs_adj += 1000
            elif dd == 1:
                obs_adj += 12
            elif dd == 2:
                obs_adj += 4
        # Also slightly reduce opponent's ability to intercept the same target.
        opp_d = cheb(nx, ny, tx, ty) - 0.35 * cheb(ox, oy, tx, ty)

        val = d_to_t + obs_adj + 0.25 * opp_d
        if val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move