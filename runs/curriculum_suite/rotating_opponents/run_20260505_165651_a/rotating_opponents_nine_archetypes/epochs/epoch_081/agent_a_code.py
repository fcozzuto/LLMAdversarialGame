def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    if not resources:
        return [0, 0]

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                valid_resources.append((x, y))
    if not valid_resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (score, tie, dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # lead score: how much earlier we can arrive vs opponent (after this step)
        # plus small bias for moving closer to the best target.
        best_res = None
        best_res_score = -10**18
        best_res_tie = None
        for tx, ty in valid_resources:
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            adv = od - sd  # positive means we are closer
            # If opponent is extremely close, prioritize starving (lower their access).
            risk = 0
            if od <= 2:
                risk = 6
            score = adv * 10 - sd - risk
            tie = (-(adv), sd, tx, ty)
            if best_res is None or score > best_res_score or (score == best_res_score and tie < best_res_tie):
                best_res_score = score
                best_res = (tx, ty)
                best_res_tie = tie

        tx, ty = best_res
        sd_now = man(nx, ny, tx, ty)
        od_now = man(ox, oy, tx, ty)
        # Final move score: emphasize positive advantage; break ties toward bigger separation.
        final_score = (od_now - sd_now) * 10 - sd_now
        tie2 = (-od_now, sd_now, nx, ny)
        if best is None or final_score > best[0] or (final_score == best[0] and tie2 < best[1]):
            best = (final_score, tie2, dx, dy)

    return [int(best[2]), int(best[3])]