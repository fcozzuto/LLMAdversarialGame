def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target resource that we can secure faster, while also being "expensive" for opponent to reach.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Maximize opponent lead disadvantage, then prefer nearer self, then deterministic by coords
        key = (do - ds, -ds, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # Prefer moves that decrease distance to our target; also slightly consider increasing opponent distance to their closest resource.
    opp_targets = resources

    opp_closest = cheb(ox, oy, opp_targets[0][0], opp_targets[0][1])
    for rx, ry in opp_targets[1:]:
        d = cheb(ox, oy, rx, ry)
        if d < opp_closest:
            opp_closest = d

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)

        # Compute how our move would affect opponent denial potential: estimate opponent's best remaining distance (static estimate).
        # Since opponent doesn't move now, we use a small penalty if our move is likely to let them reach quickly:
        # maximize (opp_dist_to_best - opp_dist_to_that_target) by choosing target with good margin already; add tiny bias to slow their approach.
        do_est = opp_closest
        score = (-ds2, -(ds2 + do_est), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]