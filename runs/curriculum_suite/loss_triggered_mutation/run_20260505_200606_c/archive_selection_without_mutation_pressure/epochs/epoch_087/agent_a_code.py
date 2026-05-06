def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def legal_steps(px, py):
        out = []
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((nx, ny))
        return out

    opp_steps = legal_steps(ox, oy)
    if not opp_steps:
        opp_steps = [(ox, oy)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the resource that gives the best "we-beat-opp" advantage,
        # assuming opponent greedily reduces their distance to that same resource.
        val = -10**18
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            if ds == 0:
                cur = 10**9
            else:
                opp_best = 10**9
                for ax, ay in opp_steps:
                    d = man(ax, ay, rx, ry)
                    if d < opp_best:
                        opp_best = d
                # Beat margin first, then punish distance.
                cur = (opp_best - ds) * 1000 - ds - (man(ox, oy, rx, ry) * 0)
            if cur > val:
                val = cur

        # Small tie-break to progress toward dense area: prefer slightly smaller sum to top few resources.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: prefer lexicographically smallest (dx,dy) by choosing lower ds+nearest opponent risk
            cur_best = 10**9
            for rx, ry in res:
                d = man(nx, ny, rx, ry)
                if d < cur_best:
                    cur_best = d
            best_nx, best_ny = sx + best_move[0], sy + best_move[1]
            best_near = 10**9
            for rx, ry in res:
                d = man(best_nx, best_ny, rx, ry)
                if d < best_near:
                    best_near = d
            if (cur_best < best_near) or (cur_best == best_near and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]