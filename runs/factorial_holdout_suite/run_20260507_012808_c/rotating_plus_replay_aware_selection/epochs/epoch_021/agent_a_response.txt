def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    center_x, center_y = (w - 1) // 2, (h - 1) // 2
    res_set = set((r[0], r[1]) for r in resources)

    if not resources:
        best = None
        for dx, dy, nx, ny in moves:
            val = manh(nx, ny, center_x, center_y)
            opp_closer = manh(nx, ny, ox, oy) - manh(sx, sy, ox, oy)
            score = -val + 0.25 * opp_closer
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best = None
    for dx, dy, nx, ny in moves:
        immediate = 2.0 if (nx, ny) in res_set else 0.0
        # choose a resource where we are relatively closer than the opponent
        best_diff = -10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            diff = od - sd
            if diff > best_diff or (diff == best_diff and od < best_opp_d):
                best_diff = diff
                best_opp_d = od
        # encourage safe progress and discourage handing an immediate capture
        opp_capture_now = 1.0 if manh(nx, ny, ox, oy) <= 1 else 0.0
        center_bias = -0.05 * manh(nx, ny, center_x, center_y)
        score = immediate + best_diff + center_bias - 0.2 * opp_capture_now
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]