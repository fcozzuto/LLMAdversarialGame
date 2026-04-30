def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_res = resources[0]
        best_score = -10**18
        for rx, ry in resources:
            my_d = cheb(sx, sy, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # Prefer resources where opponent is farther; if tie, go closer.
            score = (op_d + 1) - (my_d + 0.2 * (my_d == 0))
            if score > best_score or (score == best_score and my_d < cheb(sx, sy, best_res[0], best_res[1])):
                best_score = score
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        # No resources visible: drift toward the center while not walking into obstacles.
        tx, ty = w // 2, h // 2
        if cheb(sx, sy, tx, ty) == 0:
            tx, ty = (w - 1) - tx, (h - 1) - ty

    best_move = (0, 0)
    best_val = 10**18
    # Deterministic tie-break by delta order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(nx, ny, ox, oy)
        # Strongly prefer stepping onto a target resource if present.
        pickup_bonus = -1000 if resources and (nx, ny) == (tx, ty) else 0
        val = my_d - 0.15 * op_d + pickup_bonus
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]