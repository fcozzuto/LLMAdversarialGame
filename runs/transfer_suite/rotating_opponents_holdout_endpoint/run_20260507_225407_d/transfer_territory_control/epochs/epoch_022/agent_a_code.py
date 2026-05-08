def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    oxp, oyp = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    selfset = set((int(p[0]), int(p[1])) for p in self_terr if len(p) >= 2)
    opposet = set((int(p[0]), int(p[1])) for p in opp_terr if len(p) >= 2)
    unq = set((int(p[0]), int(p[1])) for p in unclaimed if len(p) >= 2)

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Targeting: prioritize unclaimed closer to opponent area; else press nearest opponent cell.
    if unq:
        tx, ty = min(unq, key=lambda p: (dist(p[0], p[1], oxp, oyp), p[0], p[1]))
    elif opposet:
        tx, ty = min(opposet, key=lambda p: (dist(p[0], p[1], oxp, oyp), p[0], p[1]))
    else:
        tx, ty = oxp, oyp

    # If opponent has territory, bias toward the centroid to counter center-claim style.
    if opposet:
        xs = [p[0] for p in opposet]
        ys = [p[1] for p in opposet]
        cx = sum(xs) // len(xs)
        cy = sum(ys) // len(ys)
        tx = (tx + cx) // 2
        ty = (ty + cy) // 2

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Immediate gain signals.
        gain = 0
        if (nx, ny) in opposet:
            gain += 1000  # flipping enemy territory immediately
        elif (nx, ny) in unq:
            gain += 200   # likely to claim
        elif (nx, ny) in selfset:
            gain += 5     # safe/maintain

        # Strategic shaping: move closer to target, and avoid moving away from own control too aggressively.
        d_to_t = dist(nx, ny, tx, ty)
        d_to_own = 0
        if selfset:
            # approximate own proximity by min manhattan to any owned cell corner-ish: use a few anchors deterministically
            anchors = sorted(selfset)[:3]
            d_to_own = min(dist(nx, ny, ax, ay) for ax, ay in anchors)

        # Prefer shorter path to target; penalize drifting far from own territory (prevents suicidal moves into enemy center).
        score = gain * 1.0 - 3.0 * d_to_t - 0.2 * d_to_own

        cand = [dx, dy]
        if best_score is None or score > best_score or (score == best_score and cand < best):
            best_score = score
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]