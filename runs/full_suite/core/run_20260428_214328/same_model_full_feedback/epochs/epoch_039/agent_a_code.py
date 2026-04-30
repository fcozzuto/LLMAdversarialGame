def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_dists = [man(ox, oy, rx, ry) for rx, ry in resources]
    best_move = (0, 0)
    best_score = -10**18

    # Prefer resources where we gain distance advantage over the opponent.
    # If all are losing, fall back to the closest resource, while slightly avoiding the opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        our_best_adv = -10**18
        our_best_dist = 10**9
        for i, (rx, ry) in enumerate(resources):
            d_our = man(nx, ny, rx, ry)
            d_opp = opp_dists[i]
            adv = d_opp - d_our  # positive means we are closer
            if d_our < our_best_dist:
                our_best_dist = d_our
            if adv > our_best_adv:
                our_best_adv = adv

        # If we can secure a lead (adv>0), maximize it strongly.
        # Otherwise, minimize our distance and keep a small buffer from opponent.
        dist_from_opp = man(nx, ny, ox, oy)
        if our_best_adv > 0:
            score = 1000 * our_best_adv + dist_from_opp
        else:
            score = -50 * our_best_dist + 0.5 * dist_from_opp

        # Deterministic tie-break: prefer smaller dx, then smaller dy (stable ordering already helps).
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]