def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_val = None

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # Race: choose the resource where we minimize (ourDist - oppDist)
            val = None
            for rx, ry in resources:
                ourd = man(nx, ny, rx, ry)
                oppd = man(ox, oy, rx, ry)
                d = ourd - oppd
                if val is None or d < val:
                    val = d
            # Tie-breakers: prefer closer to some resource, and slightly farther from opponent
            if val is None:
                continue
            our_best = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < our_best:
                    our_best = d
            opp_best = man(nx, ny, ox, oy)
            val2 = val * 1000 + our_best * 10 - opp_best
            if best_val is None or val2 < best_val:
                best_val = val2
                best_move = (dx, dy)
    else:
        # No resources: move to increase distance from opponent while avoiding obstacles
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            if best_val is None or d > best_val:
                best_val = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]