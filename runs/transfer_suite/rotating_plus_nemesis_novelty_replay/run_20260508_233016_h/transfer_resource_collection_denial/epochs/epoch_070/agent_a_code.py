def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    if not resources:
        return [0, 0]

    # One-step lookahead: choose move that maximizes "secured progress" toward a good resource
    # while also pushing the opponent further away from that same target.
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Pick best resource from the moved position according to secure arrival and denial.
        local_best_key = None
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            op_d = dist(ox, oy, rx, ry)
            secure = my_d < op_d
            # Key tries to: (1) prefer secure resources, (2) minimize my_d,
            # (3) for insecure, increase the opponent advantage to reduce its impact,
            # (4) add denial term based on who is closer.
            if secure:
                key = (0, my_d, - (op_d - my_d), rx, ry)
            else:
                key = (1, my_d - op_d, my_d, rx, ry)
            if local_best_key is None or key < local_best_key:
                local_best_key = key

        # Move preference: favor moves that improve over staying, without dithering.
        # Use the chosen local resource key as the primary signal.
        if local_best_key is None:
            continue
        # Secondary: prefer staying closer to our best local target (deterministic tie-break via coordinates).
        # We re-derive by taking the first resource coords from local_best_key tail.
        _, _, _, tx, ty = local_best_key
        # Higher is better: increase opponent-my separation after the move toward target.
        score = (dist(ox, oy, tx, ty) - dist(nx, ny, tx, ty))
        cur_score = (dist(ox, oy, tx, ty) - dist(sx, sy, tx, ty))
        move_key = (local_best_key, -score, 0 if (dx == 0 and dy == 0) else 1, rx if False else tx, ty)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best = [dx, dy]

    return best if best is not None else [0, 0]