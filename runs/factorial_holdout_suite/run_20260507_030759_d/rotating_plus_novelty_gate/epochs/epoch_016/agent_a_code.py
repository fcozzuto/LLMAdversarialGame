def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # Simple deterministic: move away from opponent while staying valid
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (man(nx, ny, ox, oy), -nx, -ny)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Consider a small deterministic subset to stay fast
    rs = sorted(resources, key=lambda r: (r[0], r[1]))
    targets = rs[:10] if len(rs) > 10 else rs

    best = (0, 0)
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_gain = None
        best_res_d = None
        for rx, ry in targets:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            gain = opp_d - self_d  # positive means we'd be closer than opponent
            if best_gain is None or gain > best_gain or (gain == best_gain and self_d < best_res_d):
                best_gain = gain
                best_res_d = self_d

        if best_gain is not None and best_gain >= 0:
            # Prefer being first on a resource; tie-break by faster collection and grid-alignment
            v = (2, best_gain, -best_res_d, -ny, -nx)
        else:
            # If we can't get ahead, minimize our distance to the currently-closest "high value" resource
            dists = [(man(nx, ny, rx, ry), man(ox, oy, rx, ry), rx, ry) for (rx, ry) in targets]
            dists.sort()
            d, od, rx, ry = dists[0]
            v = (1, -d, -od, ry, rx)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]