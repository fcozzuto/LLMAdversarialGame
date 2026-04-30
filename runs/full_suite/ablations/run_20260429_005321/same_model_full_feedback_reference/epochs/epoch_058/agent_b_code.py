def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If no resources, maximize distance from opponent while moving safely.
    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = d2(nx, ny, ox, oy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Greedy: choose move that improves our advantage toward the best contested resource.
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Score all resources and take best "advantage" achieved by this move.
        best_adv = None
        for rx, ry in resources:
            my = d2(nx, ny, rx, ry)
            opp = d2(ox, oy, rx, ry)
            # Prefer moving toward resources we are closer to than opponent; also bias toward nearer ones.
            adv = (opp - my) * 4 - my + (d2(nx, ny, w / 2, h / 2) * 0.02)
            if best_adv is None or adv > best_adv:
                best_adv = adv
        # Secondary: if equal, prefer staying away from opponent a bit.
        val = best_adv * 1.0 + d2(nx, ny, ox, oy) * 0.01
        if best_move is None or val > best_move[0]:
            best_move = (val, dx, dy)
    return [best_move[1], best_move[2]] if best_move else [0, 0]