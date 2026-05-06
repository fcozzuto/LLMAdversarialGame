def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # contest line: move toward the point that minimizes max(self, opp) distance
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            d1 = man(nx, ny, ox, oy)
            d2 = man(nx, ny, (sx + ox) // 2, (sy + oy) // 2)
            v = (max(d1, d2), d1)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Select a resource we can "own" (strictly closer than opponent after our step).
    best = None
    bestv = None
    for dx, dy, nx, ny in moves:
        best_res_v = None
        for rx, ry in resources:
            ds0 = man(sx, sy, rx, ry)
            do0 = man(ox, oy, rx, ry)
            ds1 = man(nx, ny, rx, ry)
            do1 = man(ox, oy, rx, ry)
            # Prefer states where we are closer than opponent; then reduce our distance; then keep away from opponent.
            own = (ds1 < do1)
            v = (
                0 if own else 1,
                ds1,
                do0 - do1,          # slight prefer for reducing opponent advantage
                man(nx, ny, ox, oy) # keep pressure but not at expense of resource distance
            )
            if best_res_v is None or v < best_res_v:
                best_res_v = v
        if best_res_v is not None:
            if bestv is None or best_res_v < bestv:
                bestv = best_res_v
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]