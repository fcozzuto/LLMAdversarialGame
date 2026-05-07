def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx = (sx + ox) // 2
        ty = (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy, nx, ny in cand:
            # head to midpoint, but also avoid getting too close if opponent is near
            v = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)) - 0.05 * man(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Choose next step that maximizes immediate "advantage" for taking a resource.
    # Advantage: how much closer we become relative to opponent (prefer secure wins).
    best = None
    bestv = None
    for dx, dy, nx, ny in cand:
        worst_away = -10**9
        best_gain = -10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            gain = (do - ds)  # positive if we're closer than opponent to that resource after our move
            # also prefer reducing our distance to the closest resource we can plausibly reach
            reach = -ds
            if gain > best_gain:
                best_gain = gain
            # penalize being far from any resource that opponent threatens
            if do <= ds + 0:
                # opponent can potentially compete; treat this resource as critical
                worst_away = max(worst_away, gain)
            else:
                worst_away = max(worst_away, -ds)
            best_gain = best_gain + 0 * reach
        # primary: maximize best_gain; secondary: maximize worst_away; tertiary: minimize distance to opponent
        v = (best_gain, worst_away, -man(nx, ny, ox, oy), -(nx * 10 + ny))
        if bestv is None or v > bestv:
            bestv = v
            best = [dx, dy]
    return best if best is not None else [0, 0]