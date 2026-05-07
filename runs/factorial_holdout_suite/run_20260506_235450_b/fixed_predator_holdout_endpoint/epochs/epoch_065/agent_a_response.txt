def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    if not resources:
        return [0, 0]

    if (sx, sy) in obstacles:
        # should not happen; try to escape deterministically
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    res_set = set(tuple(p) for p in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by targeting resources where we can arrive strictly earlier than opponent
        score = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # encourage grabbing contested/soon resources, discourage helping opponent
            if sd < od:
                s = (od - sd) * 20 - sd
            elif sd == od:
                s = 5 - sd
            else:
                s = -((sd - od) * 30 + sd)

            # slight preference for moving toward some resource even if not contested
            if s > score:
                score = s

        # tie-break: prefer moves that reduce our distance to the best contested resource
        # (computed deterministically from current resources)
        if best is None or score > best[0]:
            best = (score, dx, dy)
        elif best is not None and score == best[0]:
            if (dx, dy) < (best[1], best[2]):
                best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]