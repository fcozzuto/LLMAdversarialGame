def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        # Fallback: move away from opponent if any, else stay
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = md((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose resource where we are relatively closest vs opponent.
    best_r = resources[0]
    best_key = None
    for r in resources:
        d1 = md((sx, sy), r)
        d2 = md((ox, oy), r)
        # Prefer: we are closer (d1-d2 small), then minimize our distance, then lexicographic.
        key = (d1 - d2, d1, r[1], r[0])
        if best_key is None or key < best_key:
            best_key = key
            best_r = r

    target = best_r
    cur_d_us = md((sx, sy), target)
    cur_d_opp = md((ox, oy), target)

    # Also prefer keeping distance from opponent when tied on progress.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd_us = md((nx, ny), target)
        nd_opp = cur_d_opp  # opponent moves next; we can't predict, but we can prefer reducing their access by approaching/contesting
        progress = cur_d_us - nd_us
        # Contest bonus if we move to a position where opponent would be relatively farther.
        contest = (md((nx, ny), target) - md((ox, oy), target))
        # Avoid getting too close to opponent unless it increases progress.
        opp_dist = md((nx, ny), (ox, oy))
        val = 1000 * progress - contest + (0.1 * opp_dist)
        # Tiny deterministic tie-breaker
        val += -0.001 * (abs(dx) + abs(dy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]