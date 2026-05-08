def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = (10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and not (dx == 0 and dy == 0):
                    d = abs(nx - tx) + abs(ny - ty)
                    if d < best[0]:
                        best = (d, dx, dy)
        return [best[1], best[2]] if best[0] < 10**9 else [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                if dx != 0 or dy != 0 or True:
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # 1-step greedy "steal" policy: maximize our future advantage over opponent for the best target.
    moves.sort()  # deterministic tie-breaking order
    best_score = -10**18
    best_d = 10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        worst_self_dist = 10**18
        local_best_adv = -10**18
        local_self_dist = 10**18
        for rx, ry in resources:
            self_d = md(nsx, nsy, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - self_d  # positive => we are closer than opponent
            if adv > local_best_adv or (adv == local_best_adv and self_d < local_self_dist):
                local_best_adv = adv
                local_self_dist = self_d
        # Prefer moves that create/extend advantage; if equal, prioritize smaller self distance.
        score = local_best_adv * 1000 - local_self_dist
        if score > best_score or (score == best_score and local_self_dist < best_d):
            best_score = score
            best_d = local_self_dist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]