def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Score candidate move by 1-step advantage over the best resource for us,
    # and a penalty if it gives the opponent a large immediate advantage.
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_best = -10**9
        opp_best = -10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds
            if adv > my_best:
                my_best = adv
            # opponent "best immediate swing" if we move away from a contested point
            # (approx: assume opponent can move to any neighbor next turn)
            # use a fast lower bound on opponent distance after one move
            min_do1 = 10**9
            for odx, ody in deltas:
                ex, ey = ox + odx, oy + ody
                if not inb(ex, ey) or (ex, ey) in obstacles:
                    ex, ey = ox, oy
                min_do1 = min(min_do1, man(ex, ey, rx, ry))
            opp_adv = min_do1 - ds
            if opp_adv > opp_best:
                opp_best = opp_adv

        # Tie-breakers: prefer closer to the best target, then prefer progress towards center
        # (helps avoid stalling/dithering).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_dist = abs(nx - cx) + abs(ny - cy)
        my_closest = min(man(nx, ny, rx, ry) for rx, ry in resources)
        score = (my_best * 1000) - (opp_best * 5) - my_closest - center_dist * 0.01

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]