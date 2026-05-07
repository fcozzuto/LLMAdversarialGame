def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    res_set = set()
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
                res_set.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def resource_score(x, y):
        # Prefer resources we can reach sooner than opponent; penalize long self time.
        best = -10**9
        for rx, ry in res_set:
            st = cheb(x, y, rx, ry)
            ot = cheb(ox, oy, rx, ry)
            lead = ot - st
            # If we can land on it now, dominate.
            if st == 0:
                return 10**9
            # If we are likely to lose, still consider but strongly discounted.
            s = lead * 10 - st
            # Anti-sweep: avoid moving to same row/col band as opponent if not leading.
            if ot <= st:
                s -= 3
            # Obstacle proximity (soft)
            if obs_set:
                md = 999
                for ax, ay in obs_set:
                    d = abs(x - ax) + abs(y - ay)
                    if d < md:
                        md = d
                        if md == 0:
                            break
                s -= (2 if md <= 2 else 0) + (1 if md <= 3 else 0)
            if s > best:
                best = s
        return best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Tie-break deterministically by a fixed move order.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = resource_score(nx, ny)
        # Small preference for forward progression (reduce distance to current best resource direction)
        if resources:
            # pick a deterministic reference resource: lexicographically smallest for stability
            rx0, ry0 = min(res_set)
            val -= 0.1 * cheb(nx, ny, rx0, ry0)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If somehow all moves invalid, stay.
    return [int(best_move[0]), int(best_move[1])]