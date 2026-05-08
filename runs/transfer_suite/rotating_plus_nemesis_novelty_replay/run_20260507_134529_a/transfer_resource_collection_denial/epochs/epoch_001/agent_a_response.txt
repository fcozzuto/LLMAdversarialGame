def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    best = None
    best_val = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = sd - 0.15 * od  # prefer resources we can reach sooner
        if best is None or val < best_val or (val == best_val and (sd < best[0] or (sd == best[0] and od < best[1]))):
            best = (sd, od, rx, ry)
            best_val = val
    _, _, tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    def dist_after(dx, dy):
        nx, ny = sx + dx, sy + dy
        return cheb(nx, ny, tx, ty)

    def opp_dist_after(dx, dy):
        nx, ny = sx + dx, sy + dy
        return cheb(nx, ny, ox, oy)

    # Prefer getting closer to target; then avoid being closer to opponent.
    best_move = None
    best_key = None
    for dx, dy in moves:
        d = dist_after(dx, dy)
        od = opp_dist_after(dx, dy)
        key = (d, -od, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]