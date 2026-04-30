def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) if w and h else [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    have_res = len(resources) > 0

    # Precompute opponent's current best distance to reduce "race" outcomes.
    opp_best = 10**9
    if have_res:
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if d < opp_best:
                opp_best = d

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        score = 0
        # Favor taking/approaching nearest resource.
        if have_res:
            my_best = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < my_best:
                    my_best = d
            score += 40.0 / (1.0 + my_best)

            # If we can reach any resource "sooner" than opponent, prioritize.
            # Approx race using one-step improvement: compare my_best vs opp_best.
            score += 8.0 * (opp_best - my_best) / (1.0 + opp_best)

            # Mild deterministic preference for higher "priority" resources (top-left tie-break by coordinates).
            # This helps avoid ties looping.
            nearest = min(resources, key=lambda r: (cheb(nx, ny, r[0], r[1]), r[1], r[0]))
            score += 0.01 * (nearest[0] + nearest[1])
        else:
            # No visible resources: advance toward opponent's corner/center line for map pressure.
            score += 2.0 / (1.0 + cheb(nx, ny, ox, oy))
            score -= 0.1 * (abs(nx - center_x) + abs(ny - center_y))

        # Prefer moves that increase distance from opponent if resources are present (reduce stealing).
        if have_res:
            score += 0.15 * cheb(nx, ny, ox, oy)

        # Deterministic tie-break: keep move with lexicographically smallest (dx,dy) among equals.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]