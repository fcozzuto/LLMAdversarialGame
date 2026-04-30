def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = None

    if not resources:
        # No visible resources: move toward opponent-mirrored corner to keep pressure.
        tx, ty = (w - 1, h - 1) if (sx <= w // 2 and sy <= h // 2) else (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -dist2(nx, ny, tx, ty) - 0.01 * (nx * 10 + ny)
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Evaluate moves by advantage: how much closer we are than the opponent would be for each resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Prefer actions that create a large "reach advantage" on some resource.
        # Use max over resources; add slight preference for being nearer to any resource.
        max_adv = None
        min_own = None
        for rx, ry in resources:
            d_self = dist2(nx, ny, rx, ry)
            d_opp = dist2(ox, oy, rx, ry)
            adv = d_opp - d_self
            if max_adv is None or adv > max_adv or (adv == max_adv and (rx, ry) < (rx, ry)):
                max_adv = adv
            if min_own is None or d_self < min_own:
                min_own = d_self

        # Tie-break deterministically: prefer staying closer to resources, then lexicographic delta.
        v = float(max_adv) + (1.0 / (1.0 + min_own))
        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]