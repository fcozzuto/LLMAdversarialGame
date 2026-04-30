def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    x, y = self_pos[0], self_pos[1]
    ox, oy = opp_pos[0], opp_pos[1]

    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_v = -10**18
    any_ok = False

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        any_ok = True

        if resources:
            dres = 10**9
            max_adv = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                dso = cheb(ox, oy, rx, ry)
                if ds < dres:
                    dres = ds
                adv = dso - ds
                if adv > max_adv:
                    max_adv = adv
        else:
            dres = 0
            max_adv = 0

        opp_d = cheb(nx, ny, ox, oy)

        v = 6.0 * max_adv - 1.5 * dres - 0.05 * opp_d
        if v > best_v:
            best_v = v
            best = [dx, dy]

    if best is None:
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                return [dx, dy]
        return [0, 0]
    return best