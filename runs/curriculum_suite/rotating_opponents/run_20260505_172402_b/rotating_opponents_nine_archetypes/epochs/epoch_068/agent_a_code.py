def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = None

    # If resources are gone, retreat to maximize survival while slightly pushing toward center.
    if not resources:
        tx, ty = w // 2, h // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            # Prefer staying away from opponent, but drift to center.
            val = dist2(nx, ny, ox, oy) * 10 - dist2(nx, ny, tx, ty)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        my_opportunity = -10**18
        # Choose the resource where we can get closer than the opponent (interception bias).
        for rx, ry in resources:
            d_self = dist2(nx, ny, rx, ry)
            d_op = dist2(ox, oy, rx, ry)

            # Encourage being much closer than opponent; also prefer overall progress toward resources.
            # Small tie-breakers: keep away from opponent if equal, and lightly prefer reducing distance to nearest resource.
            tie_break = -dist2(nx, ny, ox, oy) * 0.001
            val = (d_op - d_self) * 3.0 + (-d_self) * 0.01 + tie_break

            if val > my_opportunity:
                my_opportunity = val

        # If there is a clear best opportunity, take it; otherwise bias toward opponent-approaching resources.
        # Additional drift: reduce distance to the midpoint to avoid corner_guard stagnation.
        midx, midy = (w - 1 + 0) // 2, (h - 1 + 0) // 2
        mid_d = dist2(nx, ny, midx, midy)
        val_total = my_opportunity - mid_d * 0.0005

        if best_val is None or val_total > best_val:
            best_val = val_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]