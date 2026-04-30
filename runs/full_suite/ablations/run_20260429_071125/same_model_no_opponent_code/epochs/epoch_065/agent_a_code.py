def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def md(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    my = (sx, sy)
    opp = (ox, oy)

    if not resources:
        # No visible resources: move to increase distance from opponent while staying safe
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    v = md((nx, ny), opp)
                    if v > bestv:
                        bestv = v
                        best = [dx, dy]
        return best

    # Target: take good resources, but avoid ones where opponent is clearly closer unless it's a strong "swing"
    candidates = []
    for r in resources:
        myd = md(my, r)
        opd = md(opp, r)
        # score higher is better
        # If opponent is closer by >=1, penalize; otherwise prefer closer.
        penalty = 0
        if opd + 1 < myd:
            penalty = 20 * (myd - opd)
        swing = (opd - myd)
        # Small bias toward center-ish to reduce edge stagnation
        center_bias = -abs(r[0] - (w - 1) / 2) - abs(r[1] - (h - 1) / 2)
        score = -myd - penalty + 0.8 * swing + 0.05 * center_bias
        # Tie-break deterministically by coordinates
        candidates.append((score, r[0], r[1], r))
    candidates.sort(reverse=True)
    target = candidates[0][3]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Choose move that reduces distance to target; if tie, prefer moves that deny opponent.
    best = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = md((nx, ny), target)
        opd = md(opp, target)
        # Estimate opponent reach to this cell (not actual, but useful for "denial")
        oppd_to_me = md(opp, (nx, ny))
        key = (-(myd), -(max(0, opd - myd)), oppd_to_me, -abs(nx - target[0]) - abs(ny - target[1]), -dx*1e-3 - dy*2e-3)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]