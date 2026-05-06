def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position") or (0, 0))
    ox, oy = map(int, observation.get("opponent_position") or (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    me = (sx, sy)
    opp = (ox, oy)

    # Choose resource where we have the best "arrival lead" vs opponent.
    best_r = None
    best_val = None
    for r in resources:
        myd = man(me, r)
        opd = man(opp, r)
        lead = opd - myd  # positive means we arrive earlier (under manhattan metric)
        # Small deterministic tiebreakers to reduce oscillation.
        val = (lead, -myd, -r[0], -r[1])
        if best_val is None or val > best_val:
            best_val = val
            best_r = r

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Move one step toward target, but avoid blocked cells and prefer minimizing opponent threat.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # If we delay too much, opponent may steal: prefer actions where (opp_to_r - my_to_r) stays high.
            myd2 = abs(nx - tx) + abs(ny - ty)
            opd2 = abs(ox - tx) + abs(oy - ty)
            threat = (opd2 - myd2)
            dist_to_target = myd2
            candidates.append((threat, -dist_to_target, -nx, -ny, dx, dy))

    if candidates:
        candidates.sort(reverse=True)
        return [int(candidates[0][4]), int(candidates[0][5])]

    return [0, 0]