def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if (x, y) not in obstacles and 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    ox, oy = int(op[0]), int(op[1])

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prioritize resources I can reach no later than opponent; break ties by closer distance and then deterministically by coordinate.
    best = None
    best_key = None
    for x, y in resources:
        my_d = cheb(sx, sy, x, y)
        opp_d = cheb(ox, oy, x, y)
        # Higher is better: larger advantage; then smaller my_d; then smaller x,y deterministically.
        key = (opp_d - my_d, -my_d, -x, -y)
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for mdx, mdy in [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]:
        nx, ny = sx + mdx, sy + mdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((nx, ny, mdx, mdy))

    # Choose move that most improves the contested objective.
    if not candidates:
        return [0, 0]

    best_move = None
    best_move_key = None
    for nx, ny, mdx, mdy in candidates:
        my_d2 = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        key = (opp_d - my_d2, -my_d2, -nx, -ny)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [mdx, mdy]

    return best_move