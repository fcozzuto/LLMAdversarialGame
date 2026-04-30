def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # No resources: head toward center to avoid being boxed in
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            v = -dist
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target resource by maximizing our advantage over opponent
    def target_for_move(nx, ny):
        best_adv = -10**9
        best_res = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((nx, ny), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # prefer resources we can reach sooner than opponent; slightly reward closeness
            adv = (do - ds) * 100 - ds
            # if very close, prioritize strongly
            if ds == 0:
                adv += 10**6
            if adv > best_adv:
                best_adv = adv
                best_res = (rx, ry)
        return best_res

    best_move = [0, 0]
    best_val = -10**18
    center_x, center_y = w // 2, h // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        tr = target_for_move(nx, ny)
        if tr is None:
            continue
        rx, ry = tr
        ds = dist((nx, ny), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        adv = (do - ds) * 100 - ds

        # Discourage moving adjacent to opponent unless it increases advantage
        opp_adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1) and not (nx == ox and ny == oy)
        if opp_adj:
            adv -= 80

        # Mild center-bias to prevent drift into corners when resources are sparse
        adv += -0.5 * (abs(nx - center_x) + abs(ny - center_y))

        # Ensure determinism with a stable tie-break
        if adv > best_val or (adv == best_val and (dx, dy) < tuple(best_move)):
            best_val = adv
            best_move = [dx, dy]

    return best_move