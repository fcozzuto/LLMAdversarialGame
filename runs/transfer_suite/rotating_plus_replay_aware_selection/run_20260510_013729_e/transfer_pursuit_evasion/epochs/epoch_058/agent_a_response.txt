def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Opponent "evader" tendency: move toward the farthest corner from us, locally.
    def evader_target(px, py):
        bestc = None
        bestd = -1
        for cx, cy in corners:
            d = abs(cx - px) + abs(cy - py)
            if d > bestd:
                bestd = d
                bestc = (cx, cy)
        return bestc

    tcx, tcy = evader_target(ox, oy)
    # Determine opponent next-step intention (without needing its exact policy).
    pdx = 0 if tcx == ox else (1 if tcx > ox else -1)
    pdy = 0 if tcy == oy else (1 if tcy > oy else -1)
    intended = (ox + pdx, oy + pdy)
    if intended[0] < 0 or intended[0] >= w or intended[1] < 0 or intended[1] >= h or intended in obs:
        intended = (ox, oy)

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Prefer closing on predicted opponent position; if equal, reduce current distance.
        d_pred = abs(nx - intended[0]) + abs(ny - intended[1])
        d_now = abs(nx - ox) + abs(ny - oy)

        # Wall-run counter: avoid letting opponent "escape" further to farthest corner.
        opp_escape = abs(tcx - intended[0]) + abs(tcy - intended[1])
        # Our move that reduces opponent escape potential is slightly favored.
        escape_after = abs(tcx - nx) + abs(tcy - ny)
        # More blocking-like behavior: avoid positions with low mobility.
        mobility = 0
        for bx, by in deltas:
            tx, ty = nx + bx, ny + by
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                mobility += 1

        # Deterministic composite key (minimize). Add dx/dy magnitude to break ties.
        key = (d_pred, d_now, -escape_after + 0.001 * opp_escape, -mobility, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best