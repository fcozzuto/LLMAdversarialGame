def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        valid_moves = [(0, 0, sx, sy)]

    best_target = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in blocked:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer targets where we can be strictly closer; also prefer nearer targets and boundary control.
        can_take = (do - ds)
        edge = 1 if (rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1) else 0
        # Key: maximize can_take, then edge, then minimize ds, then deterministic tie-break by coordinates.
        key = (can_take, edge, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    rx, ry = best_target
    # Choose the move that maximizes immediate advantage to the target,
    # and slightly punishes moves that allow opponent closer by next step.
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in valid_moves:
        ns = man(nx, ny, rx, ry)
        os = man(ox, oy, rx, ry)
        my_adv = (os - ns)
        # If we are already not closer than opponent, prioritize reducing opponent's future advantage.
        # Opponent next-step estimate: best possible decrease for them among 9 moves.
        opp_best = 10**9
        for pdx, pdy in deltas:
            tx, ty = ox + pdx, oy + pdy
            if inb(tx, ty):
                opp_best = min(opp_best, man(tx, ty, rx, ry))
        opp_adv = (opp_best - ns)
        edge_move = 1 if (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1) else 0
        score = (my_adv * 100) + (edge_move * 5) - ns - max(0, opp_adv) * 2 + (dx * 0.01) + (dy * 0.005)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]