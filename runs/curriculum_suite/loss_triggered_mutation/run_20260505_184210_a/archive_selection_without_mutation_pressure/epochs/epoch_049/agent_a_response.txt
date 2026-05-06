def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Target choice: prefer resources we can reach earlier than opponent; fallback to nearest.
    best_target = None
    best_reach_gap = None
    best_d = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        gap = od - myd  # positive: we are closer
        if best_target is None or gap > best_reach_gap or (gap == best_reach_gap and (best_d is None or myd < best_d)):
            best_target = (rx, ry)
            best_reach_gap = gap
            best_d = myd

    # If no resources, drift to maximize distance from opponent (avoid being trapped).
    if best_target is None:
        scored = []
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            s = dist(nx, ny, ox, oy)
            scored.append((s, -(dx == 0 and dy == 0), dx, dy))
        scored.sort(reverse=True)
        return [scored[0][2], scored[0][3]]

    rx, ry = best_target

    # Score moves with: progress to target, avoid stepping into "deny" lanes near opponent,
    # and avoid giving opponent immediate access by staying too close.
    best = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_t = dist(nx, ny, rx, ry)
        d_o = dist(nx, ny, ox, oy)

        # Prefer smaller target distance
        val = -2 * d_t

        # Don't mirror opponent too closely; keep some separation
        if d_o <= 1:
            val -= 12
        elif d_o == 2:
            val -= 5

        # Discourage moves onto same row/col as opponent when it increases "deny" likelihood
        if ny == oy:
            val -= 4
        if nx == ox:
            val -= 4

        # If we're not yet closer than opponent to target, move to improve that gap.
        myd_next = d_t
        od_next = dist(ox, oy, rx, ry)
        gap = od_next - myd_next
        val += 3 * gap

        # Small deterministic tie-break: prefer moves that increase x then y
        tie = (dx, dy)
        if best_val is None or val > best_val or (val == best_val and tie > best[0]):
            best_val = val
            best = (tie, dx, dy)

    return [best[1], best[2]]