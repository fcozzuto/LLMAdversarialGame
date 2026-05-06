def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacle_set = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    dirs = [d for d in dirs if not (d[0] == 0 and d[1] == 0)] + [(0, 0)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacle_set:
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a resource we can contest: maximize (opp_d - self_d), then prefer smaller self_d, then tie-break by coords.
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, -abs(rx - 3.5) - abs(ry - 3.5), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # Desired step toward target
    want_dx = 0 if tx == x else (1 if tx > x else -1)
    want_dy = 0 if ty == y else (1 if ty > y else -1)

    # Score candidate moves by progress to target while keeping opponent farther (denial)
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacle_set:
            continue

        self_to = cheb(nx, ny, tx, ty)
        opp_to = cheb(ox, oy, tx, ty)

        # Lower self_to is better; higher opp_to is better.
        # Also bias toward the exact desired direction when safe.
        dir_bias = 0
        if dx == want_dx:
            dir_bias += 1
        if dy == want_dy:
            dir_bias += 1
        if dx == want_dx and dy == want_dy:
            dir_bias += 2

        val = (opp_to - self_to) * 100 - self_to * 3 + dir_bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]