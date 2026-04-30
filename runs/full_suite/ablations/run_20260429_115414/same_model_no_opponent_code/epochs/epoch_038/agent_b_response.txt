def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_options():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    yield dx, dy

    deltas = list(step_options())
    if not deltas:
        return [0, 0]

    if resources:
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to (or tie), otherwise still allow but penalize.
            score = (1 if sd <= od else 0, -sd if sd <= od else sd, sd + od, rx, ry)
            # Deterministic min
            if best is None or score < best[0]:
                best = (score, rx, ry)
        _, tx, ty = best
    else:
        # No resources visible: head to top-right-ish to stay active deterministically.
        tx, ty = w - 1, 0

    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # If contested (opponent can reach target faster), avoid giving them easy approach by not moving closer to opponent.
        contested = resources and cheb(sx, sy, tx, ty) > cheb(ox, oy, tx, ty)
        score = (d_to_t, (-(d_opp) if not contested else d_opp), abs(nx - tx) + abs(ny - ty), dx, dy)
        if score < best_move[:5]:
            best_move = (score[0], score[1], score[2], dx, dy)

    return [int(best_move[3]), int(best_move[4])]