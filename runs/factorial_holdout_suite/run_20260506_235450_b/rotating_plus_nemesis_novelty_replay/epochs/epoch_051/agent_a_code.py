def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    respos = []
    for r in resources:
        try:
            x, y = r
            respos.append((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def score_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        if respos:
            # Prefer moves that get closer to the best (by Manhattan) resource for us,
            # and also avoid giving opponent a strong advantage.
            best = 10**9
            best_opp = 10**9
            for rx, ry in respos:
                d = abs(nx - rx) + abs(ny - ry)
                if d < best:
                    best = d
                if opp_exists:
                    d2 = abs(ox - rx) + abs(oy - ry)
                    if d2 < best_opp:
                        best_opp = d2
            # Higher is better: closer to resource, and if opponent is far, that's even better.
            # Tie-breaker favors moves that directly land on a resource.
            on_res = 1 if (nx, ny) in set(respos) else 0
            adv = (best_opp - best)
            return on_res * 10**6 + (1000 - best * 10) + adv
        # No resources: head toward bottom-right corner.
        tx, ty = w - 1, h - 1
        return - (abs(nx - tx) + abs(ny - ty))

    best_move = None
    best_val = -10**18
    res_set = set(respos)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = score_for_move(dx, dy) + (1 if (nx, ny) in res_set else 0)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    if best_move is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]