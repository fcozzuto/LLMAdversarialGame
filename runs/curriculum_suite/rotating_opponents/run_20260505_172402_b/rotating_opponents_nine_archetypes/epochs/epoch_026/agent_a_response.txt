def choose_move(observation):
    sx, sy = observation["self_position"]
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

    def clamp_in_bounds(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    ox, oy = observation["opponent_position"]
    if not resources:
        return [0, 0]

    # pick move that wins race to a resource; if no good race, reposition to deny diagonals
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # obstacle proximity penalty (deterministic)
        near = 0
        for (ox2, oy2) in obs:
            dd = cheb(nx, ny, ox2, oy2)
            if dd <= 1:
                near += (2 - dd) + 1
        safety = -3 * near

        # evaluate top few resources by race advantage
        local_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # higher is better: be strictly closer; also slightly prefer earlier capture (smaller my_d)
            score = (opp_d - my_d) * 12 - my_d * 2
            # mild preference for resources closer to center-ish to avoid dead corners
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score -= int(abs(rx - cx) + abs(ry - cy)) * 0.1
            if score > local_best:
                local_best = score

        # denial term: discourage moving in the same diagonal direction as opponent toward us
        ddx = sx - ox
        if ddx != 0: ddx = 1 if ddx > 0 else -1
        ddy = sy - oy
        if ddy != 0: ddy = 1 if ddy > 0 else -1
        denial = 0
        if (dx, dy) == (ddx, ddy) and cheb(nx, ny, sx, sy) > 0:
            denial -= 8

        val = local_best + safety + denial
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]