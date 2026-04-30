def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Deterministic tie-breaking order for evaluation results
    deltas_order = {d: i for i, d in enumerate(deltas)}

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate one-step move by advantage on the best contested resource
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer capturing/approaching resources; also reduce opponent advantage.
        # We assume greedy contest: consider candidate resources and maximize (opp_dist - self_dist),
        # but only if the resource is reasonably reachable soon.
        total = 0
        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Immediate capture strongly encouraged
            if sd == 0:
                score = 10**9
            else:
                # Advantage margin; closer to target and farther from opponent is better
                margin = (od - sd)
                # Penalize being too far to matter (keeps us from making useless detours)
                reach_pen = sd * sd
                score = margin * 100 - reach_pen
                # Slight preference for moving toward center when tied
                cx_pen = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
                score -= int(cx_pen)

            # Prefer higher score; deterministic tie by resource coords
            if score > local_best or (score == local_best and (rx, ry) < best_move):
                local_best = score

        # Secondary term: avoid getting boxed by obstacles by preferring moves with more valid neighbors
        neighbors = 0
        for ax, ay in deltas:
            tx, ty = nx + ax, ny + ay
            if valid(tx, ty):
                neighbors += 1
        total = local_best + neighbors * 3

        if total > best_val:
            best_val = total
            best_move = (dx, dy)
        elif total == best_val:
            if deltas_order[(dx, dy)] < deltas_order[best_move]:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]