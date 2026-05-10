def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def step_valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    r += 1
        return r

    if not resources:
        return [0, 0]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if step_valid(nx, ny):
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    # Deterministic preference ordering for tie-breaks
    # (diagonal, then straight-ish) but stable by coordinates
    candidates.sort(key=lambda t: (t[0], t[1]))

    best = None
    for dx, dy, nx, ny in candidates:
        best_for_move = None
        my_adj = 0
        for rx, ry in resources:
            rx = int(rx); ry = int(ry)
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # If we can reach now (or already on resource), strongly prioritize
            if my_d == 0:
                score = -10_000
            else:
                # advantage: smaller is better; negative means opponent closer
                advantage = my_d - op_d
                # also prefer smaller my distance, and slightly discourage risk/oscillation
                score = advantage * 1000 + my_d * 10 + risk(nx, ny) * 3
            if best_for_move is None or score < best_for_move:
                best_for_move = score
                my_adj = my_d
        # Secondary tie-breaks: fewer risk, closer-to-something, and avoid moving away from opponent too much
        if best is None or (best_for_move, risk(nx, ny), my_adj, dx, dy) < (best[0], best[1], best[2], best[3], best[4]):
            best = (best_for_move, risk(nx, ny), my_adj, dx, dy)

    return [best[3], best[4]]