def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (w // 2, h // 2)

    # If resources exist, move toward closest resource while keeping some distance from opponent
    if resources:
        best = (0, 0)
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny):  # allow staying or moving into free cell only
                continue
            if (nx, ny) in obstacles:
                continue
            # score: prefer closer to a resource, but avoid getting too close to opponent
            closest_r = min(dist((nx, ny), r) for r in resources) if resources else 0
            near_opp = dist((nx, ny), (ox, oy))
            score = -closest_r * 2
            # discourage moving into square too close to opponent
            if near_opp == 0:
                score -= 50
            else:
                score += near_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: drift toward center but keep some distance from opponent
    best = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_center = dist((nx, ny), center)
        d_opp = dist((nx, ny), (ox, oy))
        score = -d_center * 2 + d_opp
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]