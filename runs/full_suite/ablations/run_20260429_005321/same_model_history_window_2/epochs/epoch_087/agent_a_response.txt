def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (d[0], d[1]))  # deterministic order

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    best_move = (0, 0)
    best_score = -10**18

    # Choose move by maximizing "resource advantage" (opp closer minus us closer),
    # plus a small tie-break for moving toward that resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If we can step onto a resource, take it decisively.
        if (nx, ny) in set(resources):
            return [dx, dy]

        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            # If both are equally far, prefer reducing distance to win next step.
            tie = -0.01 * sd
            local_best = adv + tie if adv > local_best - 1e-9 else local_best
            # (small deterministic adjustment below)
        # Extra: discourage drifting away from all resources
        min_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        score = local_best - 0.001 * min_self

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif abs(score - best_score) <= 1e-12:
            # deterministic tie: smallest dx then dy by sorted order
            pass

    return [int(best_move[0]), int(best_move[1])]