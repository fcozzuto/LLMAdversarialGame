def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestv or (d == bestv and (dx, dy) < best):
                bestv = d
                best = (dx, dy)
        return [best[0], best[1]]

    def dist(a, b):  # manhattan
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_target = resources[0]
    best_adv = -10**9
    best_selfd = 10**9
    for r in resources:
        sd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_selfd) or (adv == best_adv and sd == best_selfd and (r[0], r[1]) < (best_target[0], best_target[1])):
            best_adv = adv
            best_selfd = sd
            best_target = r

    tx, ty = best_target[0], best_target[1]
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        od = abs(nx - ox) + abs(ny - oy)
        curd = abs(sx - tx) + abs(sy - ty)
        delta = curd - nd  # positive is progress
        # Favor progress; tie-break toward staying ahead of opponent; avoid getting too close to opponent.
        val = 1000 * delta + 5 * best_adv - nd - 0.1 * od
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]