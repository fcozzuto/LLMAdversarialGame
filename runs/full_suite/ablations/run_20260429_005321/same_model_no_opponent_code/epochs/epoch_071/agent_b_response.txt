def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no resources, just drift away from opponent to reduce interference.
    if not resources:
        best = None
        for dx, dy, nx, ny in moves:
            score = -d2(nx, ny, ox, oy)  # maximize distance
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Pick a target resource where we are most likely to arrive first, but avoid unsafe/entrapment via local move scoring.
    best_target = None
    for rx, ry in resources:
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        # Target advantage: positive means we are closer (d smaller), so prefer smaller ds-do.
        adv = ds - do
        # Tie-breaker: prefer resources far from obstacles to reduce immediate block risk.
        near_obs = 0
        for tx in (rx - 1, rx, rx + 1):
            for ty in (ry - 1, ry, ry + 1):
                if (tx, ty) in obstacles:
                    near_obs += 1
        score = adv + 2.0 * near_obs
        if best_target is None or score < best_target[0]:
            best_target = (score, rx, ry)
    _, tx, ty = best_target

    # Evaluate one-step moves by the resulting advantage and local safety.
    best = None
    for dx, dy, nx, ny in moves:
        my = d2(nx, ny, tx, ty)
        oy2 = d2(ox, oy, tx, ty)
        # Advantage: smaller my than opponent's to the same target is good.
        # Also prefer moves that increase our distance from opponent to disrupt collision races.
        opp_dist = d2(nx, ny, ox, oy)
        # Safety: count blocked neighbors around next cell.
        blocked = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                    blocked += 1
        # Strongly discourage "cornering" ourselves (high blocked).
        score = (oy2 - my) + 0.01 * opp_dist - 0.05 * blocked
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]