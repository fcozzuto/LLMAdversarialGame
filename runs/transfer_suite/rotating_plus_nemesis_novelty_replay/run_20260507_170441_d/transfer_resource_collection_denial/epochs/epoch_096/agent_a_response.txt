def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obst.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Select best target resource: prioritize resources we can reach sooner than opponent.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my = dist8(sx, sy, rx, ry)
        opp = dist8(ox, oy, rx, ry)
        # key: win-the-race (opp-my), then closer, then farther from opponent
        key = (opp - my, -my, opp)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # No visible resources: press toward opponent corner
        tx = w - 1 if sx < w - 1 - sx else 0
        ty = h - 1 if sy < h - 1 - sy else 0
        best_key = (-10**9, -10**9, 0, 0)
        ans = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            my = dist8(nx, ny, tx, ty)
            opp = dist8(nx, ny, ox, oy)
            key = (-my, -opp, -abs(nx - tx), -abs(ny - ty))
            if key > best_key:
                best_key = key
                ans = (dx, dy)
        return [int(ans[0]), int(ans[1])]

    tx, ty = best_t
    # Choose step: minimize distance to target; among ties, maximize distance to opponent.
    ans = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my = dist8(nx, ny, tx, ty)
        opp = dist8(nx, ny, ox, oy)
        # primary: get to target quickly; secondary: deny opponent; tertiary: stable toward target
        key = (-my, -(opp - my), -opp, -abs(nx - tx) - abs(ny - ty))
        if best_key is None or key > best_key:
            best_key = key
            ans = (dx, dy)
    return [int(ans[0]), int(ans[1])]