def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not res:
        return [0, 0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_key = (-10**18, 10**18, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        min_d_self = 10**9
        best_adv_for_move = -10**9
        # Choose resource that maximizes relative advantage (opp closer -> worse)
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if d_self < min_d_self:
                min_d_self = d_self
            adv = d_opp - d_self
            if adv > best_adv_for_move:
                best_adv_for_move = adv
            elif adv == best_adv_for_move and d_self < min_d_self:
                best_adv_for_move = adv

        # Key: maximize advantage, then minimize self distance to some resource (approx via min_d_self), then prefer progressing right/up? deterministic.
        key = (best_adv_for_move, -min_d_self, dx * 10 + dy)
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]) or (key[0] == best_key[0] and key[1] == best_key[1] and key[2] > best_key[2]):
            best_key = key
            best_move = [dx, dy]

    return best_move