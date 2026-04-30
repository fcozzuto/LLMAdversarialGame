def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by): 
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def valid(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles
    if not resources:
        # fallback: move away from opponent if possible
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv:
                bestv = v; best = [dx, dy]
        return best
    # Choose a target resource that we can reach sooner than the opponent (contest)
    target = None
    best_metric = None
    for rx, ry in resources:
        dself = cheb(sx, sy, rx, ry)
        dopp = cheb(ox, oy, rx, ry)
        metric = (dopp - dself) * 3 - dself  # prioritize contested and nearer
        if target is None or metric > best_metric:
            target = (rx, ry); best_metric = metric
    tx, ty = target
    # If target is far behind opponent, switch bias: go to nearest resource to us (anti-stall)
    d_to_target_self = cheb(sx, sy, tx, ty)
    d_to_target_opp = cheb(ox, oy, tx, ty)
    if d_to_target_opp - d_to_target_self > 3:
        # we are clearly ahead: still go to target but avoid opponent
        avoid_opp = True
    else:
        avoid_opp = False
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Move quality: closer to target, plus obstacle-safe and anti-collision
        dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        # Penalize moving into squares that are too close to opponent when not ahead
        penalty = 0
        if avoid_opp and opp_dist <= 2:
            penalty += (3 - opp_dist) * 4
        if not avoid_opp and opp_dist <= 1:
            penalty += 6
        # Small preference to improve: don't oscillate by preferring staying if already optimal
        score = -dist - penalty
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move