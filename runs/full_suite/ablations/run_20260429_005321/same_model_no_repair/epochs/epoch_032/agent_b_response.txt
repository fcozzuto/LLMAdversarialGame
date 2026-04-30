def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Pick a target resource where we are relatively closer than opponent (prefer strongly).
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        score = (do - ds) * 100000 - ds * 9 - (rx * 17 + ry * 3)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    _, tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    # Also consider a simple "block where it helps" term: reduce chance opponent gets even closer.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d1 = man(nx, ny, tx, ty)
        d0 = man(sx, sy, tx, ty)

        # Opponent reachability after our move (estimate): smaller distance is better for us,
        # but if it lets opponent close in a lot, penalize.
        opp_after = min(resources and [man(ox, oy, r[0], r[1]) for r in resources] or [10**9])
        opp_to_tx = man(ox, oy, tx, ty)
        # Penalize if we move away from target (worsens), and if opponent is already much closer.
        val = d1 * 100 + max(0, (opp_to_tx - d1)) * 3
        val += (d1 - d0) * 50  # discourage moving away
        # Prefer positions that have fewer blocked adjacent cells (avoid getting trapped near obstacles).
        adj_blocks = 0
        for ax, ay in deltas:
            px, py = nx + ax, ny + ay
            if not inb(px, py) or (px, py) in obs:
                adj_blocks += 1
        val += adj_blocks * 4
        # Small deterministic tie-break toward lower (x,y) to keep determinism.
        val += (nx * 1000 + ny)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]