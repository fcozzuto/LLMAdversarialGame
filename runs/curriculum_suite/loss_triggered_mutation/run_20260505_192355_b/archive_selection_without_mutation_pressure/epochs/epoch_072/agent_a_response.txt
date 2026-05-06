def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Choose the resource that maximizes our advantage over opponent, then score the move by improvement.
        best_adv = -10**9
        best_our = 10**9
        best_opp = 10**9
        for rx, ry in resources:
            d_our = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # Advantage: how much closer we are than opponent (positive is good).
            adv = d_opp - d_our
            if adv > best_adv or (adv == best_adv and (d_our < best_our or (d_our == best_our and d_opp < best_opp))):
                best_adv, best_our, best_opp = adv, d_our, d_opp

        # Also compute overall closeness and deny factor (if opponent is closer to many resources).
        our_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            our_min = min(our_min, man(nx, ny, rx, ry))
            opp_min = min(opp_min, man(ox, oy, rx, ry))

        # Composite score: prioritize beating opponent on a resource, then being close ourselves,
        # while preventing moves that help opponent's likely targets too much.
        # Denier heuristic: if opponent is already very close to some resource, prefer moves that reduce our disadvantage.
        deny = 0
        for rx, ry in resources:
            d_our = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_opp + 1 < d_our:
                deny += 1

        score = (best_adv, -our_min, -opp_min, deny, -abs(nx - ox) - abs(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]