def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = (w - 1) if sx < (w - 1) // 2 else 0
        ty = (h - 1) if sy < (h - 1) // 2 else 0
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    our_corner = (0, 0)
    opp_corner = (w - 1, h - 1)

    # Choose action that maximizes advantage on the best target resource.
    best_move = [0, 0]
    best_score = -10**9
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue

        # Risk: being too close to opponent.
        opp_d = dist(nx, ny, ox, oy)
        risk = 0
        if opp_d <= 1:
            risk += 6
        elif opp_d <= 2:
            risk += 2

        # Target race: pick resource where we are (or become) more likely to be first.
        # Score is max over resources of (opp_dist - self_dist) minus our distance to that resource.
        best_adv = -10**9
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources closer to our corner than opponent's corner (deterministic spatial bias).
            bias = 0
            if dist(rx, ry, our_corner[0], our_corner[1]) <= dist(rx, ry, opp_corner[0], opp_corner[1]):
                bias += 1
            adv = (od - sd) + bias
            # Also slightly discourage long paths even if advantage is positive.
            adv -= 0.05 * sd
            if adv > best_adv:
                best_adv = adv

        # If we can still improve advantage, value it; otherwise focus on reducing distance to likely target.
        score = 100 * best_adv - risk
        if score > best_score:
            best_score = score
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]