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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If no resources, drift toward opponent side but keep distance from obstacles.
    if not resources:
        tx, ty = w - 1, h - 1
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -d2(nx, ny, tx, ty)
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1]) if best else [0, 0]

    # Target selection with race advantage: maximize (opp_dist - our_dist) after move.
    # Additionally, if we can enter a resource square, strongly prefer it.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        enter = (nx, ny) in set(resources)
        best_local = -10**18
        for rx, ry in resources:
            our = d2(nx, ny, rx, ry)
            opp = d2(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; stronger if within 1 step.
            adv = (opp - our)
            finish = 2000 if our == 0 else (500 if our <= 2 else 0)
            # Small penalty if that move increases proximity to opponent resources advantage.
            best_local = max(best_local, adv + finish)
        # If move lands on a resource, dominate.
        score = best_local + (100000 if enter else 0) + (-d2(nx, ny, ox, oy) // 50)
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))

    return list(best[1]) if best else [0, 0]