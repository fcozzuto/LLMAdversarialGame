def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_m(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Race score: choose the resource that maximizes opponent-vs-self advantage after this move.
        # Advantage = (opp_dist - self_dist); we also penalize being far in absolute terms.
        local_best = -10**18
        for rx, ry in resources:
            sd = dist_m(nx, ny, rx, ry)
            od = dist_m(ox, oy, rx, ry)
            adv = od - sd
            sc = adv * 1000 - sd * 3 - od * 1
            if sc > local_best:
                local_best = sc

        if best_score is None or local_best > best_score:
            best_score = local_best
            best_move = [dx, dy]
        elif local_best == best_score:
            # Deterministic tie-break: prefer smaller dx, then smaller dy, then lexicographic by order in moves.
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move