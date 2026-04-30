def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource():
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; if not, prefer those where opponent is farther.
            key = (do - ds, -ds, -rx - ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_resource()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        valid_moves.append((dx, dy, nx, ny))

    if not valid_moves:
        return [0, 0]

    if target is None:
        # No resources: drift toward center while avoiding obstacles.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for dx, dy, nx, ny in valid_moves:
            key = (-(abs(nx - cx) + abs(ny - cy)), -(dx == 0 and dy == 0))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    tx, ty = target
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in valid_moves:
        ds_new = cheb(nx, ny, tx, ty)
        do_new = cheb(ox, oy, tx, ty)
        # Aggressive: maximize our advantage and reduce our distance.
        score = (do_new - ds_new) * 100 - ds_new
        # Small preference: avoid staying still unless necessary.
        if dx == 0 and dy == 0:
            score -= 0.1
        # Deterministic tie-break: favor lexicographically smaller delta among equal scores.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]