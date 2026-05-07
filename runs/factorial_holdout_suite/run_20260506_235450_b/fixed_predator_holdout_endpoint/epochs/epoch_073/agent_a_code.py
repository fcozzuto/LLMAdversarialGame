def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick the next target deterministically: maximize (opp advantage + progress).
    # Then choose the move that reduces our distance to that target; tie-break by keeping
    # farther from the obstacle-clutter and by improving global heuristic.
    best_target = None
    best_val = None
    for tx, ty in res:
        my_d = manh(sx, sy, tx, ty)
        opp_d = manh(ox, oy, tx, ty)
        adv = opp_d - my_d  # positive means we are closer
        # Prefer closer reachable cells, and also slightly prefer those that are not too far for us.
        val = (adv, -my_d, tx, ty)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        my_d = manh(nx, ny, tx, ty)
        opp_d = manh(ox, oy, tx, ty)
        # Encourage denying: maximize (opp_d - my_d) and secondarily reduce our distance.
        # Add a small term that prefers staying within bounds near dense resources.
        density = 0
        for rx, ry in res:
            density += 1 if manh(nx, ny, rx, ry) <= 3 else 0

        score = (opp_d - my_d, -my_d, density, -abs((nx + ny) - (sx + sy)), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]