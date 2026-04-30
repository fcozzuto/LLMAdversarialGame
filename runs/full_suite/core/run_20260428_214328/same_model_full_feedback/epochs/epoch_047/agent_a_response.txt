def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy

    # If no visible resources, steer to center-ish while keeping distance from opponent.
    if not resources:
        tx, ty = w // 2, h // 2
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            v = -md((nx, ny), (tx, ty)) - (1 if (nx, ny) == (ox, oy) else 0) + 0.1 * md((nx, ny), (ox, oy))
            if v > bestv or (v == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    # Choose move that maximizes "I am closer than opponent" for some resource,
    # while avoiding getting too close to opponent.
    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        my_next = (nx, ny)
        my_to_opp = md(my_next, (ox, oy))
        # Prefer actions that secure a resource I'm relatively closer to.
        best_for_move = -10**18
        for r in resources:
            myd = md(my_next, r)
            opd = md((ox, oy), r)
            # Primary: maximize advantage opd - myd; Secondary: minimize myd.
            adv = opd - myd
            val = adv * 10 - myd
            # Strongly prefer immediate resource capture.
            if myd == 0:
                val += 10**6
            # Avoid moves that let opponent immediately capture the same resource next.
            if opd == 1 and myd > 1:
                val -= 200
            if val > best_for_move:
                best_for_move = val
        # Opponent pressure term.
        if my_to_opp <= 1:
            best_for_move -= 150
        else:
            best_for_move += 0.5 * my_to_opp
        if best_for_move > best_val or (best_for_move == best_val and (dx, dy) < best_move):
            best_val, best_move = best_for_move, (dx, dy)

    return [best_move[0], best_move[1]]