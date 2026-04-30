def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Choose a resource where we have the greatest distance advantage over opponent.
    target = None
    best_adv = -10**30
    if resources:
        for rx, ry in resources:
            ds = dist2(sx, sy, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Advantage: opponent far, we close. Slightly prefer shorter actual path too.
            adv = (do - ds) - (0.05 * ds) + (0.01 * do)
            if adv > best_adv:
                best_adv = adv
                target = (rx, ry)
    else:
        target = None

    # If no resources, move to maximize distance from opponent.
    if target is None:
        best = None
        best_val = -10**30
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = dist2(nx, ny, ox, oy)
            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val
        return list(best if best is not None else (0, 0))

    rx, ry = target

    # Intercept bias: if opponent is closer to this target, we try to move toward it anyway
    # but also favor moves that increase our distance from opponent.
    opp_closer = dist2(ox, oy, rx, ry) < dist2(sx, sy, rx, ry)

    best_move = (0, 0)
    best_score = -10**30
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Prefer moving closer to target.
        to_t = dist2(nx, ny, rx, ry)
        score = -to_t
        # If opponent closer, also deny space by moving away from opponent.
        if opp_closer:
            score += 0.25 * dist2(nx, ny, ox, oy)
        # Strongly prefer stepping onto a resource.
        if (nx, ny) in resources:
            score += 10**9
        # Tiny deterministic tie-break: prefer smaller dx then smaller dy.
        score += -0.0001 * abs(dx) - 0.00001 * abs(dy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]