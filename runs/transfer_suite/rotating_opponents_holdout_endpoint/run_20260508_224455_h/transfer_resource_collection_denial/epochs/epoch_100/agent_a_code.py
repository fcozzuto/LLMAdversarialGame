def choose_move(observation):
    gw = int(observation["grid_width"]); gh = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def dist(a, b): 
        dx = a[0] - b[0]; dx = -dx if dx < 0 else dx
        dy = a[1] - b[1]; dy = -dy if dy < 0 else dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for r in resources:
        x, y = int(r[0]), int(r[1])
        if inb(x, y) and (x, y) not in obs:
            myd = dist((sx, sy), (x, y))
            opd = dist((ox, oy), (x, y))
            lead = opd - myd
            res.append((x, y, lead, myd, opd))
    if not res:
        return [0, 0]

    # Prefer resources where we are closer than opponent (lead>0); otherwise slowest to lose.
    res.sort(key=lambda t: (-t[2], t[3], t[4], t[0], t[1]))
    best = res[0]
    bx, by = best[0], best[1]

    # One-step greedy with deterministic tie-break; include slight penalty if move worsens our lead.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd1 = dist((nx, ny), (bx, by))
        base = -myd1
        # Denier-ish: prefer staying ahead of opponent at the target and not stepping into being left behind.
        opd1 = dist((ox, oy), (bx, by))
        lead1 = opd1 - myd1
        score = base + 2.0 * lead1
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]