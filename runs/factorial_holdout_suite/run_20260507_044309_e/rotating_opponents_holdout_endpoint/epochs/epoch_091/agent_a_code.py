def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if safe(nx, ny):
                return [dx, dy]
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny):
            my_moves.append((dx, dy))

    opp_dist = dist((sx, sy), (ox, oy))
    # Strategy: for each move, choose the resource that gives best lead advantage, with opponent-distance pressure.
    best = None
    best_val = None
    for dx, dy in my_moves:
        nx, ny = sx + dx, sy + dy

        # Prefer resources that are closer to us than opponent, but still reachable quickly.
        best_lead = None
        best_self_d = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            lead = sd - od
            if best_lead is None or lead < best_lead or (lead == best_lead and (best_self_d is None or sd < best_self_d)):
                best_lead = lead
                best_self_d = sd

        # Secondary objective: increase distance from opponent to reduce their sweep efficiency.
        d_opp_after = abs(nx - ox) + abs(ny - oy)
        val = (best_lead, best_self_d, -d_opp_after, abs(dx) + abs(dy))

        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]