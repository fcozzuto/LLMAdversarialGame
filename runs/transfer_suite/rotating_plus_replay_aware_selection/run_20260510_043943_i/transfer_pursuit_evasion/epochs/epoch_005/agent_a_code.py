def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("hunter" in self_role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    def density(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                c += 1
        return c

    def neighbors_free(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    # Predict opponent (assume evader behavior: maximize distance from us)
    opp_moves = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if valid(nx, ny):
            opp_moves.append((dx, dy, nx, ny))
    if not opp_moves:
        px, py = ox, oy
    else:
        best = None
        for dx, dy, nx, ny in opp_moves:
            score = (dist2(nx, ny, sx, sy), neighbors_free(nx, ny), -density(nx, ny), -nx - 10 * ny)
            cand = (score, dx, dy, nx, ny)
            if best is None or cand > best:
                best = cand
        px, py = best[3], best[4]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if is_pursuer:
            d = dist2(nx, ny, px, py)
            score = (-d, neighbors_free(nx, ny), -density(nx, ny), -nx - 10 * ny)
        else:
            d = dist2(nx, ny, ox, oy)
            score = (d, -density(nx, ny), neighbors_free(nx, ny), nx + 10 * ny)
        cand = (score, dx, dy, nx, ny)
        if best_move is None or cand > best_move:
            best_move = cand
    if best_move is None:
        return [0, 0]
    return [best_move[1], best_move[2]]