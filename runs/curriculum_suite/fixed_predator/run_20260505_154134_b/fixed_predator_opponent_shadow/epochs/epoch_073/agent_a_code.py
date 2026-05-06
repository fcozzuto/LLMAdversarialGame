def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Target: resource with best (opponent closeness advantage) and not too far
    best = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        key = (od - sd, -sd, -cx, -cy)  # larger is better
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)
    tx, ty = best

    cand_best = [0, 0]
    cand_best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                nx, ny = sx, sy
            # score components
            d_to_target = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # encourage moving toward some resource in case target becomes irrelevant
            d_res = 10**9
            for cx, cy in resources:
                d = cheb(nx, ny, cx, cy)
                if d < d_res:
                    d_res = d
            # higher score is better
            score = (d_opp * 3) - (d_to_target * 2) - d_res
            # tie-break deterministically: prefer progress toward target, then away from opponent
            tie = (d_to_target, -d_opp, dx, dy)
            if cand_best_score is None or score > cand_best_score or (score == cand_best_score and tie < cand_best_tie):
                cand_best = [dx, dy]
                cand_best_score = score
                cand_best_tie = tie
    return cand_best