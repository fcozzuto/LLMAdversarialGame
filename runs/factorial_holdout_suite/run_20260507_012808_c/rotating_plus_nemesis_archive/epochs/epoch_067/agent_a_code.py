def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = w - 1 - ox, h - 1 - oy
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        best = [0, 0, 10**9]
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - tx) + abs(ny - ty)
                if d < best[2]:
                    best = [ddx, ddy, d]
        return [best[0], best[1]]

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    # If standing on a resource, stay (deterministically).
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Choose a resource where we are not behind (or least behind), tie-break by remaining distance.
    best = None  # (score, rx, ry)
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # score higher is better; primary prefer we are closer than opponent, then absolute closeness.
        score = (10 - (ds - do)) * 100 - ds
        if best is None or score > best[0] or (score == best[0] and (rx, ry) < (best[1], best[2])):
            best = (score, rx, ry)
    _, tx, ty = best

    # Move one step toward target; if blocked, pick neighbor minimizing distance to target, with deterministic tie-break.
    dx = 0 if sx == tx else (1 if sx < tx else -1)
    dy = 0 if sy == ty else (1 if sy < ty else -1)

    cand = [(dx, dy)]
    # add alternate diagonal/axis steps for robustness
    if dx != 0 and dy != 0:
        cand += [(dx, 0), (0, dy), (dx, -dy if dy != 0 else 0), (-dx if dx != 0 else 0, dy)]
    cand += [(0, 0)]
    # evaluate unique in deterministic order
    seen = set()
    best_move = None  # (dist, dx, dy)
    for ddx, ddy in cand + deltas:
        if (ddx, ddy) in seen:
            continue
        seen.add((ddx, ddy))
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        key = (d, ddx, ddy)
        if best_move is None or key < best_move:
            best_move = key
    return [int(best_move[1]), int(best_move[2])]