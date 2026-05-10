def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-(10**18), 0, 0)

    # heuristic targets: prioritize unclaimed, otherwise resources, otherwise contest opponent
    nearest_resource = None
    if resources:
        bestd = 10**18
        for r in resources:
            d = dist2((sx, sy), r)
            if d < bestd:
                bestd = d
                nearest_resource = r

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in blocked:
            continue

        cell = (nx, ny)
        score = 0

        if cell in unclaimed:
            score += 100
        elif cell in oppT:
            score += 60
        elif cell in selfT:
            score += 5
        else:
            score += -2

        score += -0.8 * dist2(cell, (cx, cy))  # central pressure

        if nearest_resource is not None:
            score += 3.0 * (dist2((sx, sy), nearest_resource) - dist2(cell, nearest_resource))

        # slight preference to move closer to opponent territory if no unclaimed/resources
        if nearest_resource is None and not resources and not unclaimed:
            if oppT:
                bestd = 10**18
                for t in oppT:
                    d = dist2(cell, t)
                    if d < bestd:
                        bestd = d
                score += -0.01 * bestd

        # deterministic tie-break: fixed ordering already; keep highest score
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]