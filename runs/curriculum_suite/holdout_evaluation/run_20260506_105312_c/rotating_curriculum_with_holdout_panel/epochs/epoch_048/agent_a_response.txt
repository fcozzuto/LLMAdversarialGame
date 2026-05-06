def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (10**9, 0, 0)
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            # resource-denier tends to pressure; keep some separation while moving toward center of board
            sc = -cheb(nx, ny, 3.5, 3.5) + 0.15 * cheb(nx, ny, ox, oy)
            if sc < best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_dx, best_dy = 0, 0
    best_score = 10**18

    # Score moves by how likely we are to reach a resource before opponent, plus a small safety term.
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # safety: if we are close to opponent, avoid being on top of them
        safety = 0.18 * cheb(nx, ny, ox, oy)

        # target advantage: pick best resource for us considering opponent
        target_best = 10**9
        for r in resources:
            rx, ry = r[0], r[1]
            d_ours = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # prefer resources where we can arrive sooner; penalize if opponent already closer
            adv = (d_ours - d_opp)
            # if contested, prefer resources with smaller absolute ours distance
            val = adv * 2.0 + d_ours * 0.25
            if val < target_best:
                target_best = val

        # additional nudge: if opponent is nearer to all resources, move to the nearest "escape" cell away from opponent direction
        opp_near = 0
        for r in resources:
            rx, ry = r[0], r[1]
            if cheb(ox, oy, rx, ry) < cheb(nx, ny, rx, ry):
                opp_near += 1
        denial = 0.08 * opp_near

        score = target_best + denial - safety
        if score < best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]