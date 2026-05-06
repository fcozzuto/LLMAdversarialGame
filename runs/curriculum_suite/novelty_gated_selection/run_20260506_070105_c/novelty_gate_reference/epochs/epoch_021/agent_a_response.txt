def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_val = -10**18

    any_res = False
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            any_res = True
            break
    if not any_res:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        best_gain = -10**18
        best_opp_dist = 10**9
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = int(r[0]), int(r[1])
            if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in blocked:
                continue
            our_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            gain = opp_d - our_d  # positive means we can reach sooner than opponent
            if gain > best_gain or (gain == best_gain and opp_d < best_opp_dist):
                best_gain = gain
                best_opp_dist = opp_d
        # Encourage capturing sooner, and also avoid drifting too far from viable claims
        val = best_gain * 100 - (abs(nx - sx) + abs(ny - sy)) + (-abs(ox - nx) - abs(oy - ny)) * 0.01
        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best