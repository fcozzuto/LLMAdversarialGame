def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def greedy_step(px, py, tx, ty):
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if blocked(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return best

    if not resources:
        dx = -1 if sx > ox else (1 if sx < ox else 0)
        dy = -1 if sy > oy else (1 if sy < oy else 0)
        return [dx, dy]

    cx = (gw - 1) / 2.0
    cy = (gh - 1) / 2.0

    best_move = (0, 0)
    best_val = -10**18

    for dx0, dy0 in moves:
        nx, ny = sx + dx0, sy + dy0
        if blocked(nx, ny):
            continue
        center_pen = cheb(nx, ny, cx, cy) * 0.01

        # Pick the best target given this move, but score by advantage over opponent.
        val = -center_pen
        for rx, ry in resources:
            mydist = cheb(nx, ny, rx, ry)
            odx, ody = greedy_step(ox, oy, rx, ry)
            ox2, oy2 = ox + odx, oy + ody
            oppdist = cheb(ox2, oy2, rx, ry)

            advantage = oppdist - mydist  # positive => we are closer after both act
            # Strong preference for winning proximity races; mild bias against distance.
            cand = advantage * 10.0 - mydist
            if cand > val:
                val = cand

        if val > best_val:
            best_val = val
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]