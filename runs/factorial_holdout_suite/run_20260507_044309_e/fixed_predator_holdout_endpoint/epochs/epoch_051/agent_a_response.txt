def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        best_adv = -10**9
        best_self_d = 10**9
        best_opp_d = 10**9

        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we get there first (denial/steal)
            if adv > best_adv:
                best_adv = adv
                best_self_d = sd
                best_opp_d = od
            elif adv == best_adv:
                if sd < best_self_d:
                    best_self_d = sd
                    best_opp_d = od
                elif sd == best_self_d and od < best_opp_d:
                    best_self_d = sd
                    best_opp_d = od

        # Opportunistic steal when possible; otherwise deny nearest-to-opponent resource.
        score = best_adv * 1000 - best_self_d * 3 + (best_opp_d == 0) * 5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]