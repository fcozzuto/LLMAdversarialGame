def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if not resources:
        # Fallback: move away from opponent a bit, and drift toward center deterministically
        cx, cy = w // 2, h // 2
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -md((nx, ny), opp) + 0.2 * md((nx, ny), (cx, cy))
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose move that improves my access to best resource while discouraging opponent from the same target.
    # Deterministic tie-breaking: prefer lexicographically smallest delta among equal scores.
    opp_weight = 1.15
    center = (w // 2, h // 2)
    best = None
    bestv = None

    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        my_pos = (nx, ny)
        # Evaluate against resources; pick the best achievable "competitive" target
        local_best = None
        for r in resources:
            d_me = md(my_pos, r)
            d_op = md(opp, r)
            # If opponent is already much closer, heavily penalize letting them "win" the target.
            # Lower is better; convert to higher-is-better.
            score = d_me - opp_weight * max(0, d_op - d_me)
            # Small center preference to break ties meaningfully
            score += 0.02 * md(my_pos, center)
            if local_best is None or score < local_best:
                local_best = score
        # Also consider direct opponent pressure to avoid being "cornered"
        opp_pressure = -0.03 * md(my_pos, opp)
        v = -local_best + opp_pressure
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]