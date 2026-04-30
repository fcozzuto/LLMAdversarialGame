def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Two-stage: pick candidate resources by who is likely to arrive first, then move to improve that.
    cand = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prefer resources we are closer to; if behind, prefer those far from opponent to contest later
        ahead = od - sd
        cand.append((ahead, sd, od, rx, ry))
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    top = cand[:min(6, len(cand))]  # small and deterministic

    best_move = [0, 0]
    best_val = -10**18
    best_sd_after = 10**9

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate by best contest utility among candidates
        local_best = -10**18
        local_sd = 10**9
        for _, _, _, rx, ry in top:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            utility = (od - sd) * 10 - sd  # big weight to being closer than opponent
            # add slight bias away from letting opponent get nearer than us next
            utility -= max(0, sd - od) * 5
            if utility > local_best:
                local_best = utility
                local_sd = sd

        if local_best > best_val or (local_best == best_val and local_sd < best_sd_after):
            best_val = local_best
            best_sd_after = local_sd
            best_move = [dx, dy]

    return best_move