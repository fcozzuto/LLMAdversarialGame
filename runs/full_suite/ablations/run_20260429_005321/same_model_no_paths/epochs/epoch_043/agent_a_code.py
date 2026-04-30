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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Choose a deterministic focus resource: nearest to us, tie by lexicographic.
    if resources:
        focus = None
        bestd = None
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if bestd is None or d < bestd or (d == bestd and (x, y) < focus):
                bestd = d
                focus = (x, y)
    else:
        focus = (ox, oy)

    fx, fy = focus

    # Evaluate each move: prefer closer to focus; also discourage moves that let opponent get closer.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        my_d = cheb(nx, ny, fx, fy)

        opp_d = cheb(ox, oy, fx, fy)
        # Compute opponent best response distance after our move, assuming opponent can move anywhere valid
        # but without simulating their policy, just a conservative estimate using one-step min.
        best_opp_next = opp_d
        for odx, ody in deltas:
            onx, ony = ox + odx, oy + ody
            if inside(onx, ony):
                d2 = cheb(onx, ony, fx, fy)
                if d2 < best_opp_next:
                    best_opp_next = d2

        # Main score: lower my_d is better; higher (best_opp_next - my_d) is better.
        # Add small term to avoid stepping adjacent to opponent if they are closer to focus.
        adj = 0
        if cheb(nx, ny, ox, oy) == 1:
            adj = 1

        val = -my_d * 100 + (best_opp_next - my_d) * 20 - adj * 5
        # Deterministic tie-break: prefer staying still then lexicographic order.
        if val > best_val:
            best_val = val
            best = (dx, dy)
        elif val == best_val:
            if (dx, dy) == (0, 0) and best != (0, 0):
                best = (dx, dy)
            elif best != (0, 0) and (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]