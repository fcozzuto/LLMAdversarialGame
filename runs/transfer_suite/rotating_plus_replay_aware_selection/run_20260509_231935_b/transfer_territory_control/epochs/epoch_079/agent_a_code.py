def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    self_territory = observation.get("self_territory") or []
    opp_territory = observation.get("opponent_territory") or []
    selfT = set()
    oppT = set()
    for p in self_territory:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            selfT.add((int(p[0]), int(p[1])))
    for p in opp_territory:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    unC = set()
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            unC.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_list = list(oppT) if oppT else [tuple(observation["opponent_position"])]
    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0
        if not inside(nx, ny) or (nx, ny) in obs:
            score = -10**9
        else:
            base = 0.0
            if (nx, ny) in oppT:
                base += 6.0
            elif (nx, ny) in selfT:
                base += 1.0
            elif (nx, ny) in unC:
                base += 2.0
            else:
                base += 0.5

            md = 10**9
            for ax, ay in opp_list:
                d = man(nx, ny, ax, ay)
                if d < md:
                    md = d
            base += (4.0 - 0.7 * md)

            my_center = -0.03 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            base += my_center

            score = base

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]