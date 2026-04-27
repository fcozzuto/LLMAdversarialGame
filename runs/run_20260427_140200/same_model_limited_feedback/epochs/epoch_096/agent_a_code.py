def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy  # Chebyshev for 8-neighbor

    if resources:
        best = None
        best_key = None
        for i, r in enumerate(resources):
            rx, ry = r
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources where we are closer; break ties deterministically by position then index
            key = (do - ds, -ds, -rx, -ry, -i)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic preference ordering: iterate fixed moves list
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Score: closer to target, also avoid moving into cells that are likely too "contestable" by opponent
        cur_ds = dist((nx, ny), (tx, ty))
        cur_do = dist((ox, oy), (tx, ty))
        # If opponent can match/beat our progress, slightly deprioritize
        # Also small penalty if we move onto/near opponent (discourage collisions)
        opp_near = max(abs(nx - ox), abs(ny - oy))
        score = (-cur_ds, cur_do - cur_ds, -opp_near, -abs(dx) - abs(dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]