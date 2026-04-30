def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy  # Chebyshev for diagonal moves

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)

    if resources:
        my = (sx, sy)
        enemy = (ox, oy)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            nm = (nx, ny)
            score = 0
            for r in resources:
                d_my = dist(my, r)
                d_en = dist(enemy, r)
                d_my2 = dist(nm, r)
                # Prefer targets where we get (or keep) an advantage, and reduce our distance.
                adv_before = d_en - d_my
                adv_after = d_en - d_my2
                if adv_after < 0:
                    continue  # don't chase targets we can't catch after the move
                score += 100 * (adv_after - adv_before) - d_my2
            # Add light bias to closer overall when no improving catches exist
            if score == 0:
                # deterministic "nearest resource" fallback
                score = -min(dist((nx, ny), r) for r in resources)
            if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)
        return [best[1], best[2]]

    # No resources visible: move toward center while staying valid.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    bestd = 10**9
    bestmove = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist((nx, ny), (cx, cy))
        if d < bestd or (d == bestd and (dx, dy) < bestmove):
            bestd = d
            bestmove = (dx, dy)
    return [bestmove[0], bestmove[1]]