def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)
    turns_remaining = int(observation.get("turns_remaining", 0))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            v = dist(ox, oy, cx, cy) - 0.01 * dist(sx, sy, cx, cy)
            if best is None or v > best[0]:
                best = (v, cx, cy)
        tx, ty = best[1], best[2]
        return [0 if tx == sx else (1 if tx > sx else -1), 0 if ty == sy else (1 if ty > sy else -1)]

    res = [(int(r[0]), int(r[1])) for r in resources]
    res_set = set(res)

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If we can collect a resource immediately, strongly prioritize it.
        imm = 1.0 if (nx, ny) in res_set else 0.0

        # Evaluate best "win" on any resource from the next position.
        best_gap = -10**9
        best_self_time = 10**9
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            gap = od - sd  # positive => we can reach earlier (or tie advantage)
            if gap > best_gap:
                best_gap = gap
                best_self_time = sd
            elif gap == best_gap and sd < best_self_time:
                best_self_time = sd

        # Secondary: reduce opponent's best possible gap by moving into contested lines.
        # (Approximate) compute opponent best gap after our move assuming opponent just continues optimally:
        opp_best_gap = -10**9
        for rx, ry in res:
            od = dist(ox, oy, rx, ry)
            sd = dist(nx, ny, rx, ry)
            gap = od - sd
            if gap > opp_best_gap:
                opp_best_gap = gap

        # Tertiary: keep moving toward our currently best resource direction (deterministic nudge).
        # Choose target as argmax of gap, tie by smallest sd.
        tx, ty = res[0]
        tgap = None
        tsd = None
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            gap = od - sd
            if tgap is None or gap > tgap or (gap == tgap and sd < tsd):
                tgap = gap
                tsd = sd
                tx, ty = rx, ry
        nudge = -(dist(nx, ny, tx, ty) * 0.001)

        # Combine. Encourage taking immediate resources, then maximizing reach advantage.
        # Later in the game, emphasize gaps less and self-time more to secure remaining.
        time_weight = 0.6 if turns_remaining > 20 else 1.0
        val = (imm * 1000.0) + (best_gap * 50.0) + (-(best_self_time) * time_weight) + (opp_best_gap * 0.0) + nudge

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]