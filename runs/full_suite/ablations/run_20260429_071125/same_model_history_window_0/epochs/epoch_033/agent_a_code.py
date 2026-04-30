def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1 - ox, h - 1 - oy
    else:
        best = None
        best_d = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = king_dist(sx, sy, rx, ry)
            do = king_dist(ox, oy, rx, ry)
            # Prefer resources where we are comparatively closer; break ties by being closer and then by position.
            key = (ds - do, ds, rx, ry)
            if best is None or key < best:
                best = key
                best_d = (rx, ry)
        tx, ty = best_d if best_d else resources[0]

    # Choose move that is valid and improves target; include a mild blocking bias toward preventing opponent approaches.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = king_dist(nx, ny, tx, ty)
        d_opp_after = king_dist(nx, ny, ox, oy)
        # Blocking heuristic: avoid moves that give opponent a very short route to the target.
        d_opp_to_target = king_dist(ox, oy, tx, ty)
        key = (d_to_target, -d_opp_after, d_opp_to_target, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]