def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def best_target(px, py, want_adv):
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in occ:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => we are closer
            # want_adv: pick highest adv; tie-break toward center and closeness
            key = (-adv if want_adv else adv, ds, cheb(rx, ry, cx, cy), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry, adv, ds, do)
        return best

    opp_best = best_target(ox, oy, want_adv=True)
    # Choose a target that we can reach earlier than opponent if possible; otherwise deny center.
    my_best = best_target(sx, sy, want_adv=True)
    if my_best is not None:
        tx, ty, adv, ds, do = my_best
        # If opponent is strictly closer to everything, push toward opponent's nearest resource instead.
        if opp_best is not None and adv < 0:
            tx, ty, _, _, _ = opp_best
    else:
        tx, ty = cx, cy

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            nx, ny = sx, sy
            dx, dy = 0, 0

        ds_next = cheb(nx, ny, tx, ty)
        # Offensive: increase advantage vs chosen target.
        adv_next = cheb(ox, oy, tx, ty) - ds_next

        # Defensive: push away from opponent's best target to reduce their capture speed.
        if opp_best is not None:
            ex, ey, _, _, _ = opp_best
            opp_dist_next = cheb(ox, oy, ex, ey)  # constant for our move, so instead use effect on them by moving toward blocking cell
            # Simple proxy: distance from our position to opponent's target (smaller means we are more likely to contest).
            contest = cheb(nx, ny, ex, ey)
        else:
            contest = 0

        # Tie-breakers: prefer staying central and moving off our current cell when equal.
        center = cheb(nx, ny, cx, cy)
        moved = 0 if (dx == 0 and dy == 0) else 1
        score = (-adv_next, ds_next, center, contest, -moved)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]