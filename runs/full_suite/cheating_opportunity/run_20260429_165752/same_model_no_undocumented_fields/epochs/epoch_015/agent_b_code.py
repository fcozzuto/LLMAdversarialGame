def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            ex, ey = int(o[0]), int(o[1])
            if 0 <= ex < w and 0 <= ey < h:
                obstacles.add((ex, ey))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_val = -10**18
    best_tie = (10**9, 10**9)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate move by the best relative race advantage among all remaining resources.
        # Primary: maximize (opp_dist - self_dist). Secondary: keep us close to that chosen resource.
        local_best = (-10**18, 10**9, 10**9)  # (adv, self_d, opp_d)
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            cand = (adv, sd, od)
            if cand > local_best:
                local_best = cand

        adv, sd, od = local_best
        tie = (sd, od)
        if adv > best_val or (adv == best_val and tie < best_tie):
            best_val = adv
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]