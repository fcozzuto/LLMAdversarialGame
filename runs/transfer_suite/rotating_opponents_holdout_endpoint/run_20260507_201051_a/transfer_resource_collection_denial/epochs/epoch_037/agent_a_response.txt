def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        best = (-(10**9), 0, 0)
        bestm = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = man(nx, ny, ox, oy)
            # Prefer moves that increase distance; slight tie-break to drift toward farthest corner.
            corner_bias = (nx == w - 1 or nx == 0) + (ny == h - 1 or ny == 0)
            cand = (v, corner_bias, 0)
            if cand > best:
                best = cand
                bestm = [dx, dy]
        return bestm

    # Pick the best next move by how it changes "win likelihood" on the best available resource.
    best = (-(10**18), -10**9, 0)
    bestm = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # For this next position, measure advantage over opponent on the most favorable resource.
        # Advantage = opp_dist - self_dist (bigger is better). Penalize if opponent is already strictly closer.
        best_adv = -(10**18)
        closest_self = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Discourage targets where opponent is already much closer.
            if od < sd:
                adv -= 2
            if sd < closest_self:
                closest_self = sd
            if adv > best_adv:
                best_adv = adv

        # Tie-break: prefer reducing our distance to the closest remaining resource,
        # and keep diagonal/orthogonal progress consistent by preferring larger step toward resource.
        # (Deterministic, simple.)
        tie = -closest_self
        cand = (best_adv, tie, -(dx * dx + dy * dy))
        if cand > best:
            best = cand
            bestm = [dx, dy]
    return bestm