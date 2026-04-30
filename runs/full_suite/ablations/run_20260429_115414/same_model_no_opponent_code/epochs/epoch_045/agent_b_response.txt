def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = (w // 2, h // 2)
    if resources:
        best = None
        for rx, ry in resources:
            my_d = cheb(sx, sy, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            penalty = 0.0
            if my_d > op_d:
                penalty = 0.8 * (my_d - op_d)
            # tiny deterministic bias to avoid ties
            bias = 0.001 * ((rx * 17 + ry * 31) % 100)
            key = my_d + penalty + bias
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_next = cheb(nx, ny, tx, ty)
        op_next = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target, while not walking into opponent proximity.
        val = my_next - 0.35 * op_next
        if cheb(nx, ny, ox, oy) <= 1:
            val += 2.5
        # slight preference for moves that also improve along the target direction deterministically
        step_prog = (cheb(sx, sy, tx, ty) - my_next)
        val -= 0.12 * step_prog
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]