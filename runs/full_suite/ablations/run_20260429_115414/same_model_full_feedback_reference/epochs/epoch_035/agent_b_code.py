def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles
    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Pick resource we can "claim" (not slower than opponent), else pick closest.
    target = None
    if resources:
        best = None
        for r in resources:
            dS = md(my_pos, r)
            dO = md(opp_pos, r)
            claim = dS - dO  # <=0 means we are at least as fast in Manhattan metric
            # Prefer: claim <=0; then smallest dS; then largest slack dO-dS; then deterministic tie by coords
            key = (0 if claim <= 0 else 1, dS, -(dO - dS), r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        target = best[1]

    # If no resources visible, drift to the nearest corner away from opponent while avoiding obstacles.
    if target is None:
        corners = [(0, 0), (0, H - 1), (W - 1, 0), (W - 1, H - 1)]
        # pick corner that maximizes distance from opponent, then minimizes distance from self
        target = None
        best = None
        for c in corners:
            if valid(c[0], c[1]):
                dO = md(opp_pos, c)
                dS = md(my_pos, c)
                key = (-dO, dS, c[0], c[1])
                if best is None or key < best:
                    best = key
                    target = c
        if target is None:
            target = my_pos

    # Choose move that reduces distance to target; break ties by distancing from opponent; avoid worse resources.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        npos = (nx, ny)
        dT = md(npos, target)
        dO = md(npos, opp_pos)
        # Additional: if resources exist, prefer moving closer to any resource we can claim.
        claim_bonus = 0
        for r in resources[:]:  # small list typically
            dS = md(npos, r)
            dOpp = md(opp_pos, r)
            if dS <= dOpp:
                # closer claimed resource is better
                claim_bonus = max(claim_bonus, 8 - dS)
        key = (dT, -dO, -claim_bonus, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]