def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs_set.add((px, py))

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                res_list.append((rx, ry))
    if not res_list:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def mdist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = (gw - 1) / 2.0, (gh - 1) / 2.0
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
        # Local 1-step lookahead: choose the best resource from the landing position.
        # Emphasize winning races (opp_dist - self_dist), then prefer nearer and some center control.
        local_best = -10**9
        for tx, ty in res_list:
            sd = mdist(nx, ny, tx, ty)
            od = mdist(ox, oy, tx, ty)
            adv = od - sd
            # If opponent is closer, still consider contesting but with reduced weight.
            # This helps against deniers without random blocking.
            contest = adv
            if adv < 0:
                contest = int(contest * 2 - sd * 0.5)
            tie = -sd - 0.01 * (abs(tx - center[0]) + abs(ty - center[1]))
            s = contest * 1000 + tie
            if s > local_best:
                local_best = s
        # If we can reach a resource immediately, prioritize that strongly.
        imm = 0
        for tx, ty in res_list:
            if mdist(nx, ny, tx, ty) == 0:
                imm = 200000
                break
            if mdist(nx, ny, tx, ty) == 1:
                imm = max(imm, 60000 - (abs(tx - ox) + abs(ty - oy)))
        score = local_best + imm + 0.0001 * (-(abs(nx - center[0]) + abs(ny - center[1])))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move