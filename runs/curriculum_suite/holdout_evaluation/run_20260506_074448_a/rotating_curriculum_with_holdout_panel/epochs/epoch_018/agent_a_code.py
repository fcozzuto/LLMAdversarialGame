def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def center_bias(x, y):
        cx = w // 2
        cy = h // 2
        d = cheb(x, y, cx, cy)
        return -d  # closer to center is better

    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        mb = center_bias(nx, ny) * 0.35
        score = mb
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can contest; avoid those opponent is much closer to
            reach_adv = (do - dm) * 1.8
            # Extra penalty if we are behind and can't catch quickly
            behind_pen = 0
            if do < dm:
                if dm - do >= 3:
                    behind_pen = 3.2
                elif dm - do >= 1:
                    behind_pen = 1.2
            # Slight preference for nearer reachable resources
            near_bonus = 1.0 / (1 + dm)
            score = score + (reach_adv + near_bonus) - behind_pen
        # Prefer fewer moves taken implicitly by higher dm effect through reach_adv; add slight direct term
        score = score - cheb(nx, ny, sx, sy) * 0.01
        if score > best[2]:
            best = (dx, dy, score)

    return [best[0], best[1]]