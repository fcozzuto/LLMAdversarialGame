def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    tr = observation.get("turns_remaining", 1)
    tr = tr if isinstance(tr, int) else int(tr)

    # Target selection: prefer resources where we are at least as close as opponent;
    # else prefer biggest distance advantage over opponent (i.e., opponent farther).
    best = None
    best_sc = -10**18
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        can_take = 1 if myd <= opd else 0
        # Early: contest more; late: speed more.
        speed_w = 0.6 + 0.4 * min(max(tr, 0), 50) / 50.0
        contest_w = 1.6 - speed_w
        # Small obstacle proximity penalty to reduce getting stuck.
        adj = 0
        for ax, ay in ((rx - 1, ry), (rx + 1, ry), (rx, ry - 1), (rx, ry + 1),
                        (rx - 1, ry - 1), (rx + 1, ry - 1), (rx - 1, ry + 1), (rx + 1, ry + 1)):
            if (ax, ay) in obstacles:
                adj += 1
        sc = (can_take * 5000) + (opd - myd) * (2.0 * contest_w) - myd * (1.0 * speed_w) - adj * 0.15
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    tx, ty = best
    # Candidate moves: try to reduce distance to target, avoid obvious obstacle hits.
    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            deltas.append((dx, dy))
    deltas.append((0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Order candidates deterministically by (distance after move), then lexicographic dx,dy.
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_after = man(nx, ny, tx, ty)
        candidates.append((d_after, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [dx, dy]