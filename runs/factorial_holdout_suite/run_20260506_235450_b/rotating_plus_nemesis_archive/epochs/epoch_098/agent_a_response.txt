def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        best_for_move = None
        my_best = None
        for rx, ry in resources:
            my_steps = cheb(nx, ny, rx, ry)
            opp_steps = cheb(ox, oy, rx, ry)
            adv = my_steps - opp_steps  # smaller is better (am I earlier?)
            # Prefer taking a resource before opponent; also prefer shorter paths.
            cand = (adv, my_steps, rx, ry)
            if best_for_move is None or cand < best_for_move:
                best_for_move = cand
                my_best = my_steps
        if best_for_move is None:
            continue
        # Tie-break deterministically by preferring less movement, then lexicographic.
        move_key = (best_for_move[0], best_for_move[1], abs(dx) + abs(dy), dx, dy, nx, ny)
        if best is None or move_key < best:
            best = move_key
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move