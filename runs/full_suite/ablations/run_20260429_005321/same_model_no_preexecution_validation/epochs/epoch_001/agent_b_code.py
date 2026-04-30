def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    dxs = (-1, 0, 1)
    def cheb(a, b, c, d):
        adx = a - c
        bdy = b - d
        return adx if adx >= 0 else -adx if adx < 0 else bdy if bdy >= 0 else -bdy
    def chebys(a, b, c, d):
        adx = a - c
        if adx < 0: adx = -adx
        bdy = b - d
        if bdy < 0: bdy = -bdy
        return adx if adx > bdy else bdy
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    if not resources:
        ox2, oy2 = ox, oy
        best = (0, 0)
        best_key = None
        for dx in dxs:
            for dy in dxs:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                opp_dist = chebys(nx, ny, ox2, oy2)
                key = (-opp_dist, abs(dx) + abs(dy))
                if best_key is None or key < best_key:
                    best_key = key
                    best = (dx, dy)
        return [best[0], best[1]]

    best_target = None
    best_score = None  # higher is better
    for rx, ry in resources:
        ds = chebys(sx, sy, rx, ry)
        do = chebys(ox, oy, rx, ry)
        score = (do - ds)
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)
        elif score == best_score and ds < chebys(sx, sy, best_target[0], best_target[1]):
            best_target = (rx, ry)

    tx, ty = best_target
    options = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist_to = chebys(nx, ny, tx, ty)
            dist_opp = chebys(nx, ny, ox, oy)
            on_resource = 1 if (nx, ny) == (tx, ty) else 0
            # primary: reduce distance to target; secondary: get on target; then keep away from opponent
            key = (dist_to, -on_resource, -dist_opp, abs(dx) + abs(dy))
            options.append((key, dx, dy))
    if not options:
        return [0, 0]
    options.sort(key=lambda t: t[0])
    _, dx, dy = options[0]
    return [int(dx), int(dy)]