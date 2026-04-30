def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # No resources visible: drift to center-ish while not walking into obstacles.
        target_x, target_y = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer moving away from opponent slightly while approaching center
            score = -(cheb(nx, ny, ox, oy)) + (-abs(nx - target_x) - abs(ny - target_y))
            if score > best[0] or (score == best[0] and (dx, dy) == (0, 0)):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Score moves by best "resource to contest" advantage plus slight distance tie-breakers.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_score = -1e18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Advantage: smaller myd than opd is good; also encourage getting there sooner.
            adv = (opd - myd)
            # If we can reach this much sooner, prioritize strongly.
            s = adv * 1200 - myd * 30 + (rx + ry) * 0  # deterministic stable
            if s > move_score:
                move_score = s

        # Small preference to not just maximize advantage, but also reduce my distance to the best resource overall.
        # Deterministic tie-break: prefer staying still only if equal.
        if move_score > best_score or (move_score == best_score and (dx, dy) == (0, 0)):
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]