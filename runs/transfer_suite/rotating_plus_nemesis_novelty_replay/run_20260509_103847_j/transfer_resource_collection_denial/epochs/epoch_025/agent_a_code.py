def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (None, None)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue

        # Two-ply deterministic heuristic:
        # Choose the resource that maximizes our advantage after this move.
        best_adv = None
        best_selfd = None
        best_opppick = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # prefer resources we are at least as close to as opponent; otherwise still take best advantage
            key_adv = (0 if sd <= od else 1, -adv, sd, od)
            if best_adv is None or key_adv < (best_adv, best_selfd, best_opppick, best_opppick):
                best_adv = key_adv[0]
                best_selfd = sd
                best_opppick = od

        # Secondary scoring: if opponent is adjacent to any resource we could take next, prioritize blocking by moving closer
        adj_resource = 0
        for rx, ry in resources:
            if man(nx, ny, rx, ry) == 0:
                adj_resource = 3
                break
            if man(nx, ny, rx, ry) == 1 and man(ox, oy, rx, ry) <= 1:
                adj_resource = max(adj_resource, 2)

        # Combine into a final lexicographic preference
        # Higher adv (we are closer) is better; then minimize our distance; then prefer steps that reduce opponent distance overall.
        # Compute best resource advantage explicitly for comparison
        top = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            k = (0 if adv >= 0 else 1, -adv, sd, od)
            if top is None or k < top:
                top = k
        k = (top[0], top[1], -adj_resource, top[2], top[3])
        if best[0] is None or k < best[0]:
            best = (k, (dx, dy))

    if best[1] is None:
        return [0, 0]
    dx, dy = best[1]
    return [dx, dy]