def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
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

    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    # Prefer staying closer to resources that the opponent is slower to reach.
    if not resources:
        # Move to the center-ish while avoiding obstacles.
        target = (w // 2, h // 2)
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = cheb(nx, ny, target[0], target[1])
                if best is None or v < best[0] or (v == best[0] and dx == 0 and dy == 0):
                    best = (v, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Evaluate by best attainable "advantage" over opponent across all resources.
        # Advantage favors smaller my distance and larger opponent distance.
        cur_best = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strongly prioritize resources I can reach before/near opponent.
            adv = (opd - myd) * 10 - myd
            # Slightly discourage ending adjacent to opponent when advantages are close.
            if myd == 1:
                adv -= 2
            if cur_best is None or adv > cur_best:
                cur_best = adv
        # If multiple moves tie, prefer the one that reduces my distance to the closest resource.
        if cur_best is None:
            continue
        if best_score is None or cur_best > best_score:
            best_score = cur_best
            best_move = [dx, dy]
        elif cur_best == best_score:
            # Tie-break: minimize distance from next to nearest resource, then deterministically prefer smaller |dx|+|dy|.
            def nearest_dist(ax, ay):
                md = None
                for rx, ry in resources:
                    d = cheb(ax, ay, rx, ry)
                    if md is None or d < md:
                        md = d
                return md if md is not None else 0
            nd_best = nearest_dist(sx + best_move[0], sy + best_move[1])
            nd_cur = nearest_dist(nx, ny)
            if nd_cur < nd_best:
                best_move = [dx, dy]
            elif nd_cur == nd_best:
                if abs(dx) + abs(dy) < abs(best_move[0]) + abs(best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]