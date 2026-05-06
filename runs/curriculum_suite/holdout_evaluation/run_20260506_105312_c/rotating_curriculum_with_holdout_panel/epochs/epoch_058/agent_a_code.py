def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = abs(nx - tx) + abs(ny - ty)
            key = (d, abs(nx - ox) + abs(ny - oy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def myd(x, y, r):
        return abs(x - r[0]) + abs(y - r[1])

    def score_pos(x, y):
        # Contest: prefer states where we are closer than opponent to some nearby resource,
        # and where the opponent is farther from the resources we are close to.
        # Also encourage immediate pickup by including strong penalty if we move away.
        top = []
        for r in resources:
            d1 = myd(x, y, r)
            d2 = myd(ox, oy, r)
            # Prioritize resources we can reach sooner; break ties by how much we beat opponent.
            key = (d1, - (d2 - d1))
            top.append((key, d1, d2, r))
        top.sort(key=lambda t: t[0])
        bestv = -10**9
        for i in range(min(6, len(top))):
            _, d1, d2, r = top[i]
            # If we can get it soon, reward; if opponent can also get it soon, reduce.
            immediate = 20 if d1 == 0 else 0
            beat = (d2 - d1)
            v = immediate + (8 - d1) * 2 + beat * 3 - (1 if d2 <= d1 + 1 else 0) * 4
            # Slightly discourage moving toward resources that the opponent is already extremely close to.
            if d2 == 0:
                v -= 30
            bestv = max(bestv, v)
        # Small center/escape bias to avoid oscillations in narrow corridors
        center_bias = -0.1 * (abs(x - w//2) + abs(y - h//2))
        return bestv + center_bias

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score_pos(nx, ny)
        # Deterministic tie-break: prefer moves that get us closer to our current best target.
        if resources:
            tx, ty = resources[0][0], resources[0][1]
        else:
            tx, ty = w // 2, h // 2
        t = (-(v), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best is None or t < best[0]:
            best = (t, dx, dy)
    return [best[1], best[2]] if best else [0, 0]