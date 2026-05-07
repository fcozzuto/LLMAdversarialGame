def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = 3, 3
        if sx < (w - 1) / 2: tx = w - 2
        if sy < (h - 1) / 2: ty = h - 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_move = (0, 0)
    best_key = (-10**9, 10**9, 10**9)

    res = [tuple(r) for r in resources]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose target that maximizes advantage; then tie-break by closeness.
        best_adv = -10**9
        best_sd = 10**9
        best_yd = 10**9
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd  # higher means we reach earlier than opponent

            # Small contest bonus when sharing a row/col tendency with opponent.
            if ry == oy:
                adv += 0.25
            if rx == ox:
                adv += 0.1

            if (adv > best_adv) or (adv == best_adv and (sd < best_sd or (sd == best_sd and abs(ry - oy) < best_yd))):
                best_adv, best_sd, best_yd = adv, sd, abs(ry - oy)

        # Overall move preference: maximize advantage; then minimize our distance to that best target.
        key = (best_adv, -best_sd, -best_yd)
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]