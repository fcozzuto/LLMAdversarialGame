def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_xy_list(lst):
        out = []
        if not lst:
            return out
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.append((int(p[0]), int(p[1])))
        return out

    resources = to_xy_list(observation.get("resources", []) or [])
    obstacles = set(to_xy_list(observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if w <= 0 or h <= 0:
        return [0, 0]

    def dist2(a, b, c, d):
        dx, dy = a - c, b - d
        return dx * dx + dy * dy

    def nearest_dist2(x, y):
        if not resources:
            return 10**18
        best = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = dist2(x, y, rx, ry)
            if d < best:
                best = d
        return best

    def greedy_step(px, py):
        bestm = (0, 0)
        bestv = -10**18
        if not resources:
            return (0, 0)
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = nearest_dist2(nx, ny)
            v = -d
            if (nx, ny) in resources:
                v += 10**9
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return bestm

    opp_dx, opp_dy = greedy_step(ox, oy)
    op_next = (ox + opp_dx, oy + opp_dy)

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d = nearest_dist2(nx, ny)
        opp_d = nearest_dist2(op_next[0], op_next[1])

        advantage = opp_d - our_d  # larger is better
        bonus = 0
        if (nx, ny) in resources:
            bonus += 10**9
        # discourage giving the opponent immediate access to the same resource
        clash = 0
        if resources and op_next in resources and (nx, ny) != op_next:
            clash = 1000
        # slight preference to move generally toward nearest resource direction
        prefer = 0
        if resources:
            rx, ry = min(resources, key=lambda r: dist2(nx, ny, r[0], r[1]))
            prefer = -(abs(rx - nx) + abs(ry - ny)) // 2

        val = advantage + bonus - clash + prefer
        if val > best[0]:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]