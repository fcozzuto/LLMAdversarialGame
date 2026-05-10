def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Select top few target resources by "reach race"
    scored = []
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        scored.append((opd - myd, -myd, -rx, -ry, rx, ry))
    scored.sort(reverse=True)
    targets = [(t[4], t[5]) for t in scored[:4]]

    # Candidate moves (deterministic order)
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    for dx0, dy0 in deltas:
        nx, ny = sx + dx0, sy + dy0
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # If we step onto a resource, prioritize it strongly
        on_res = 1 if (nx, ny) in {(int(r[0]), int(r[1])) for r in resources} else 0

        # Evaluate race advantage against opponent for the best remaining target
        # Include a small "block" term: prefer moves that keep/advance being closer than opponent.
        local_best = -10**9
        for rx, ry in targets:
            myd2 = kdist(nx, ny, rx, ry)
            opd2 = kdist(ox, oy, rx, ry)
            # As game progresses, value finishing sooner more.
            urgency = 1.0 + (0.0 if turns_remaining <= 0 else (1.0 / (1.0 + myd2 + turns_remaining * 0.01)))
            val = (opd2 - myd2) * 10.0 * urgency - myd2
            if myd2 == 0:
                val += 1e6
            local_best = val if val > local_best else local_best

        # Prefer moves that reduce distance to nearest resource slightly (stability)
        nearest = 10**9
        for rx, ry in resources:
            d = kdist(nx, ny, int(rx), int(ry))
            if d < nearest:
                nearest = d

        # Avoid walking into positions from which opponent becomes strictly faster for all top targets
        opp_threat = 0
        for rx, ry in targets:
            myd2 = kdist(nx, ny, rx, ry)
            opd2 = kdist(ox, oy, rx, ry)
            if opd2 < myd2:
                opp_threat += 1

        cand = (on_res * 1e7 + local_best - nearest - opp_threat * 1000.0, -abs(dx0) - abs(dy0), dx0, dy0)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]