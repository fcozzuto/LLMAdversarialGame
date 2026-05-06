def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -dist(nx, ny, cx, cy) - 0.02 * dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    opp_dists = []
    for r in resources:
        rx, ry = r
        opp_dists.append(dist(ox, oy, rx, ry))

    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        min_self = 10**9
        best_adv = -10**9
        for i, r in enumerate(resources):
            rx, ry = r
            sd = dist(nx, ny, rx, ry)
            if sd < min_self:
                min_self = sd
            adv = opp_dists[i] - sd
            if adv > best_adv:
                best_adv = adv
        v = 6.0 * best_adv - 0.35 * min_self - 0.02 * dist(nx, ny, ox, oy)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]