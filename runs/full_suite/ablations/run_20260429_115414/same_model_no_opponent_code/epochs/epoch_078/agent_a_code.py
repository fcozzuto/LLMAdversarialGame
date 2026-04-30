def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Move to increase distance from opponent while staying in bounds/not blocked
        best = (-10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            score = cheb(nx, ny, ox, oy)
            if score > best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # Evaluate each move by targeting a resource where we are closer than the opponent.
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        myd = cheb(nx, ny, ox, oy)
        # Prefer moving away if there's no good resource advantage
        worst_penalty = 0

        move_score = 0
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            if adv > 0:
                # Strongly prefer resources we can "claim" sooner; break ties by closeness
                move_score = max(move_score, 1000 * adv - 5 * sd)
            else:
                worst_penalty = max(worst_penalty, -adv - sd * 0.01)

        if move_score == 0:
            # No clear advantage: drift toward slightly closer resources while minimizing opponent pursuit
            # (blend: minimize opponent distance to our nearest resource, and maximize our distance from opponent)
            nearest_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            nearest_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
            move_score = 30 * (nearest_opp - nearest_self) + 0.2 * myd - worst_penalty

        # Small deterministic tie-break: prefer moves that change x before y, then lower distance to center-ish
        tie = (0.001 * (abs(nx - (w // 2)) + abs(ny - (h // 2))))
        total = move_score - tie

        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]