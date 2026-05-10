def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("pursuer" in role) or (("pursuer" in opp_role) and ("evader" not in role))
    if ("evader" in role) and ("pursuer" not in role):
        pursuer = False

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def avail(nx, ny):
        c = 0
        for dx, dy in moves:
            if free(nx + dx, ny + dy):
                c += 1
        return c

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        a = avail(nx, ny)
        if pursuer:
            # Reduce distance strongly; avoid getting stuck; prefer direct lines (diagonal/orthogonal).
            man = abs(nx - ox) + abs(ny - oy)
            val = (-1000 * d) - (20 * man) + (0.5 * a)
        else:
            # Increase distance; keep mobility; slightly prefer moving away along the larger axis.
            man = abs(nx - ox) + abs(ny - oy)
            axis_bias = 0
            if abs(nx - ox) >= abs(ny - oy):
                axis_bias = (nx - ox)
            else:
                axis_bias = (ny - oy)
            val = (1000 * d) + (5 * man) + (0.5 * a) + (0.01 * axis_bias)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer staying still last (acts like conservative), then lexicographic.
            if best_move == (0, 0) and (dx, dy) != (0, 0):
                continue
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]