def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dxs = (-1, 0, 1)
    best_move = [0, 0]
    bestv = None

    # If nothing visible, head to a corner farthest (by Manhattan) from opponent.
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (man(ox, oy, c[0], c[1]) - man(sx, sy, c[0], c[1]), -c[0], -c[1]))
    else:
        # Choose a resource where we can arrive earlier, preferring largest arrival gap, then closer.
        # (Switch from baseline Chebyshev to Manhattan to better counter row-sweeping behavior.)
        tx, ty = max(resources, key=lambda r: (man(ox, oy, r[0], r[1]) - man(sx, sy, r[0], r[1]), -man(sx, sy, r[0], r[1]), -r[0], -r[1]))

    # If multiple resources tie in arrival gap, steer away from opponent's nearest-resource.
    if resources:
        opp_target = min(resources, key=lambda r: (man(ox, oy, r[0], r[1]), r[0], r[1]))
        ix, iy = opp_target[0], opp_target[1]
    else:
        ix, iy = tx, ty

    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_self = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ix, iy)
            # Primary: minimize distance to chosen target, Secondary: increase distance from opponent's likely target.
            v = (-(d_self * 10 + man(sx, sy, tx, ty) * 0), d_opp, -abs(nx - tx) - abs(ny - ty), dx, dy)
            if bestv is None or v > bestv:
                bestv = v
                best_move = [dx, dy]

    return best_move