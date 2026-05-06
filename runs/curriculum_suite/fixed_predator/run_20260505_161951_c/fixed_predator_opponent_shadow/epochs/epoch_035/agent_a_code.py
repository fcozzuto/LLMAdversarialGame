def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy, nx, ny in moves:
            d1 = man(nx, ny, tx, ty)
            d2 = man(nx, ny, ox, oy)
            key = (d1, -d2, dx, dy)
            if key < best:
                best = key
        return [best[2], best[3]]

    best_move = (0, 0)
    best_key = None

    for dx, dy, nx, ny in moves:
        # evaluate best contested resource after this move, then lightly prefer closer targets
        best_adv = -10**18
        best_res_d = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = (od - sd)  # positive means we're closer
            if adv > best_adv or (adv == best_adv and sd < best_res_d):
                best_adv = adv
                best_res_d = sd

        # if no positive advantage exists, still progress toward the "least contested" option
        # Add slight tie-breakers to avoid dithering near obstacles.
        key = (
            -best_adv,                 # maximize advantage
            best_res_d,               # then minimize distance to that resource
            man(nx, ny, ox, oy),      # then keep some spacing from opponent
            dx, dy                     # deterministic tie-break
        )
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]