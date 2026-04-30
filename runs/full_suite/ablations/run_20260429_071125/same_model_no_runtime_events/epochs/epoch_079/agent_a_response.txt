def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Head toward center if no immediate resources
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Deterministic tie-break order preference (favor forward-ish, then stay)
    priority = {(-1,-1):0,(0,-1):1,(1,-1):2,(-1,0):3,(0,0):4,(1,0):5,(-1,1):6,(0,1):7,(1,1):8}

    center = ((w - 1) // 2, (h - 1) // 2)
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate by best reachable resource advantage after this move
        # Positive scores mean "more likely we get it than opponent"
        best_local = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)

            # If opponent is already much closer, strongly penalize
            if d_op < d_me:
                adv = (d_op - d_me)  # positive when opponent closer
                s = -300 * adv - 5 * d_me
            else:
                adv = d_op - d_me  # we are closer or equal
                # Prefer grabbing soon; also prefer resources opponent can't reach quickly
                s = 120 * adv - 10 * d_me + 3 * cheb(nx, ny, center[0], center[1])

            # Small bias against moving away from that resource
            s -= 0.5 * cheb(sx, sy, rx, ry) - 0.5 * cheb(nx, ny, rx, ry)

            if s > best_local:
                best_local = s

        # If too many threats, reduce exposure by staying closer to center/diagonal
        dist_center_now = cheb(sx, sy, center[0], center[1])
        dist_center_next = cheb(nx, ny, center[0], center[1])
        s_total = best_local - 8 * (dist_center_next - dist_center_now)

        if s_total > best_score:
            best_score = s_total
            best = (dx, dy)
        elif s_total == best_score:
            # Deterministic tie-break
            if priority[(dx, dy)] < priority.get(best, (0, 0)):
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]