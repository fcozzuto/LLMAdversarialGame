def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    try:
        rem = int(observation.get("remaining_resource_count") or 0)
    except:
        rem = 0
    late = rem <= 4

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    obs_neighbors = set()
    for (x, y) in obstacles:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    obs_neighbors.add((nx, ny))

    def move_risk(x, y):
        return 2 if (x, y) in obs_neighbors else 0

    if not resources:
        # Fallback: head toward opponent with slight wall-avoidance
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy) - move_risk(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_d0 = cheb(nx, ny, ox, oy)
        my_step_risk = move_risk(nx, ny)

        # Choose target implicitly by maximizing race advantage against opponent for each resource
        local_best = -10**18
        for rx, ry in resources:
            my_dr = cheb(nx, ny, rx, ry)
            opp_dr = cheb(ox, oy, rx, ry)
            # Prefer being earlier; tie-break by closeness; late game prefers blocking farther targets
            race = (opp_dr - my_dr)
            v = race * 12 - my_dr
            if late:
                v += (my_dr - my_d0) * 0.3  # slightly bias toward opponent interaction when resources scarce
            local_best = v if v > local_best else local_best

        # Small deterministic tie-break: prefer reducing distance to the chosen "best" resource area by using my_d0
        score = local_best - my_step_risk
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]