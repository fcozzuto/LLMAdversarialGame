def choose_move(observation):
    x, y = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        da = a - c
        if da < 0: da = -da
        db = b - d
        if db < 0: db = -db
        return da + db

    # Greedy contest-counterclaim: move to opponent-owned when possible; otherwise take unclaimed that advances toward opponent.
    best = -10**18
    best_move = [0, 0]
    order = 0
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            val = -10**18 + order
        else:
            val = 0
            if (nx, ny) in opp_terr:
                val += 50  # flip immediately
            elif (nx, ny) in unclaimed:
                val += 10
                # prefer unclaimed next to opponent territory to create pressure/lines
                for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    tx, ty = nx + ax, ny + ay
                    if inside(tx, ty) and (tx, ty) in opp_terr:
                        val += 4
                        break
            elif (nx, ny) in self_terr:
                val += 2  # prefer maintaining if contest not available

            # always reduce distance to opponent position/territory
            if opp_terr:
                nearest_opp = min((man(nx, ny, px, py) for px, py in opp_terr), default=man(nx, ny, ox, oy))
                val += -nearest_opp
            else:
                val += -man(nx, ny, ox, oy)

            # slight preference for keeping away from obstacles/edges when equal
            if nx in (0, w - 1) or ny in (0, h - 1):
                val -= 1

            val += -abs(dx) - abs(dy) * 0  # deterministic tie-bias via move order only
            val += order * 0  # keep deterministic without changing val

        if val > best:
            best = val
            best_move = [dx, dy]
        order += 1

    # If everything was blocked, stay.
    if best < -10**17:
        return [0, 0]
    return best_move