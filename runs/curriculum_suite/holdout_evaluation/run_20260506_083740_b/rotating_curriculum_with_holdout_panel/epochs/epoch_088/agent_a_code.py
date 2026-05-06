def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # deterministic edge-ish fallback: move toward nearest corner along a clear diagonal preference
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = min(corners, key=lambda c: dist(sx, sy, c[0], c[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
        # otherwise try axis/diag alternatives deterministically
        for ddx, ddy in [(dx, 0), (0, dy), (dx, dy), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if ok(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    # Opportunistic interceptor: for each move, pick target resource that yields smallest "self lead"
    # (negative means already closer; positive means behind). Tie-break by absolute self distance.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sld = 10**9
        sd = 10**9
        for rx, ry in resources:
            sd_next = dist(nx, ny, rx, ry)
            od_now = dist(ox, oy, rx, ry)
            lead = sd_next - od_now  # want most negative / smallest
            if lead < sld or (lead == sld and sd_next < sd):
                sld = lead
                sd = sd_next
        # small deterministic bias: prefer staying closer to current "best edge pressure" (opponent direction)
        opp_step_x = 0 if ox == sx else (1 if ox > sx else -1)
        opp_step_y = 0 if oy == sy else (1 if oy > sy else -1)
        bias = 0 if (dx == opp_step_x or dx == 0) else 1
        bias += 0 if (dy == opp_step_y or dy == 0) else 1
        cand = (sld, sd, bias, dx, dy)
        if best is None or cand < best:
            best = cand

    return [int(best[3]), int(best[4])]