def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        bx = 0; by = 0; bd = 10**9
        for dx, dy, nx, ny in moves:
            d = abs(nx - tx) + abs(ny - ty)
            if d < bd:
                bd = d; bx = dx; by = dy
        return [bx, by]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic contest heuristic:
    # For each candidate move, evaluate nearest resource we could reach first (margin).
    best = (None, -10**18, 10**18, 10**18)
    for dx, dy, nx, ny in moves:
        best_margin = -10**18
        best_rdist = 10**18
        best_opp = 10**18
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Encourage capturing/contesting: higher (do - ds) is better.
            margin = do - ds
            if margin > best_margin or (margin == best_margin and (ds < best_rdist or (ds == best_rdist and do < best_opp))):
                best_margin = margin
                best_rdist = ds
                best_opp = do
        # Secondary: if tie, prefer reducing our distance to the opponent (shadow/interceptor pressure).
        score_tuple = (best_margin, -best_rdist, -best_opp, -dist(nx, ny, ox, oy))
        if score_tuple > best[1:]:
            best = ((dx, dy), score_tuple[0], -score_tuple[1], -score_tuple[2])

    dx, dy = best[0]
    return [int(dx), int(dy)]