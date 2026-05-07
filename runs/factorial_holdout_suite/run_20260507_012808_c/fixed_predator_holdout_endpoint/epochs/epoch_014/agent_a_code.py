def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0))
                continue
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                moves.append((dx, dy))

    if not resources:
        tx, ty = (w // 2), (h // 2)
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            sd = abs(nx - tx) + abs(ny - ty)
            od = abs(nx - ox) + abs(ny - oy)
            v = (od - sd, -sd)
            if bestv == -10**18 or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # For each move: maximize how much closer we get to some resource than the opponent.
    # Also penalize moves that bring the opponent closer to any resource while we are not.
    best_move = (0, 0)
    best_score = (-10**18, -10**18, 10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Core: best contest advantage over all resources
        best_adv = -10**18
        my_min = 10**18
        opp_min_after = 10**18

        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
            if sd < my_min:
                my_min = sd

        # Secondary: how close opponent currently is to the closest resource that is also close to us
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            if sd <= my_min:  # tie zone
                od = dist(ox, oy, rx, ry)
                if od < opp_min_after:
                    opp_min_after = od

        # Tertiary: prefer not to move if it doesn't improve contest
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        score = (best_adv, -my_min, opp_min_after + stay_pen)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]