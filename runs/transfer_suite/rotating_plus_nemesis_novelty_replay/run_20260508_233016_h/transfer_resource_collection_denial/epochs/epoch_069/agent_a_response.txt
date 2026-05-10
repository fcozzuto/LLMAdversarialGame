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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; mirror it deterministically

        # Heuristic: maximize ability to be closer than opponent to some resource after this move.
        # If no secure resource exists, maximize "deny" margin (op_d - my_d) and then minimize my distance.
        best_r_key = None
        for rx, ry in resources:
            my_d = dist(nx, ny, rx, ry)
            op_d = dist(ox, oy, rx, ry)
            secure = my_d < op_d
            # Prefer secure first; within secure prefer smaller my_d and larger margin.
            # If not secure, prefer larger margin (deny), then smaller my_d, then smaller op_d.
            key = (0 if secure else 1, -((op_d - my_d) if not secure else (op_d - my_d)), my_d, op_d, rx, ry)
            if best_r_key is None or key < best_r_key:
                best_r_key = key

        # Also add a slight penalty for moving away from the most "attractive" resource.
        # Deterministic tie-break: position order.
        move_key = (best_r_key[0], best_r_key[1], best_r_key[2], best_r_key[3], nx, ny)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]