def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = [tuple(p) for p in observation.get("resources", [])]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # Go to farthest cell from opponent (deterministic tie-break: smallest dx,dy)
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in moves:
            v = (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If we can capture immediately, do it.
    resset = set(resources)
    imm = []
    for dx, dy, nx, ny in moves:
        if (nx, ny) in resset:
            imm.append((dx, dy, nx, ny))
    if imm:
        # Prefer one where opponent is farthest (deterministic)
        imm.sort(key=lambda t: (-man(t[2], t[3], ox, oy), t[0], t[1]))
        return [imm[0][0], imm[0][1]]

    # Evaluate each next move by the best "take-now" advantage over all resources,
    # plus a small shaping term to discourage moving closer to opponent without winning a resource.
    best = None
    bestv = -10**18
    for dx, dy, nx, ny in moves:
        self_opp_dist = man(nx, ny, ox, oy)
        best_adv = -10**18
        best_sd = 10**18
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer than opponent
            if adv > best_adv or (adv == best_adv and sd < best_sd):
                best_adv = adv
                best_sd = sd
        # Break ties towards shorter self distance and slightly towards being farther from opponent.
        v = best_adv * 1000 - best_sd + self_opp_dist * 0.1
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1]) if best else True):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]