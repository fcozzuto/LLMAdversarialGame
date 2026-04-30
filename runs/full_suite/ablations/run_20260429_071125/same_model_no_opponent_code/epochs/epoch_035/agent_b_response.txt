def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Anticipate: target opponent's nearest resource if we can reach almost as fast; otherwise take our nearest.
    opp_nearest = None
    best_od = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < best_od or (d == best_od and (rx, ry) < opp_nearest):
            best_od = d
            opp_nearest = (rx, ry)

    our_nearest = None
    best_sd = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < best_sd or (d == best_sd and (rx, ry) < our_nearest):
            best_sd = d
            our_nearest = (rx, ry)

    # Switch materially: deny first (contest opponent's nearest) if close enough; else expand from our nearest.
    target = opp_nearest if cheb(sx, sy, opp_nearest[0], opp_nearest[1]) <= best_od + 1 else our_nearest
    tx, ty = target

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer faster arrival and also prefer moves that increase separation from opponent (slight contest control).
        sep = cheb(nx, ny, ox, oy)
        score = (0, nd, -sep, dx, dy)  # deterministic tuple ordering
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]