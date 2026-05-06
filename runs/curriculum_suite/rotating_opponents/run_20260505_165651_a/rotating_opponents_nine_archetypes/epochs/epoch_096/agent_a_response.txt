def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    target = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        tempo = od - sd
        key = (tempo, -sd, -od, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            target = (rx, ry)

    rx, ry = target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None
    occ_res = set(resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_d = man(nx, ny, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        capture = 1 if (nx, ny) in occ_res else 0

        # small denier-awareness: if opponent is much closer to this target, prefer "less-bad" alternatives
        denier_pen = 0
        if opp_d < self_d:
            denier_pen = (self_d - opp_d) * 0.6

        # keep moving (tie-breaker prefers lower self distance, then toward opponent bottleneck direction)
        score = capture * 1000 - self_d * 2 + (opp_d - self_d) * 3 - denier_pen + (abs(nx - ox) - abs(sx - ox)) * -0.01
        key = (score, -self_d, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move