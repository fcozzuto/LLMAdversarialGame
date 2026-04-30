def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])[:2]
    op = observation.get("opponent_position", [0, 0])[:2]
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

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    # Target selection: nearest resource to us; if none, target opponent corner direction.
    if resources:
        tx, ty = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[1], r[0]))
    else:
        tx = 0 if ox > (w - 1) // 2 else (w - 1)
        ty = 0 if oy > (h - 1) // 2 else (h - 1)

    # Opportunistic: if opponent is closer to chosen target, shift to second-best resource.
    def res_ranking(r):
        return cheb(sx, sy, r[0], r[1]) - 0.7 * cheb(ox, oy, r[0], r[1])

    if resources:
        # pick best by relative advantage
        tx, ty = max(resources, key=res_ranking)
    else:
        tx, ty = tx, ty

    # Deterministic scoring for each move
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Gain picking resource immediately
        gain = 0
        if resources:
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    gain = 1000
                    break

        # Move toward target
        dist_t = cheb(nx, ny, tx, ty)

        # Deny opponent: increase their distance if possible
        dist_o = cheb(nx, ny, ox, oy)
        opp_to_target = cheb(ox, oy, tx, ty)
        my_to_target = dist_t

        # If opponent is closer, prioritize reducing their advantage
        # Heuristic weights tuned for deterministic behavior.
        score = gain
        score += -1.2 * dist_t
        score += 0.35 * dist_o
        score += 0.7 * (opp_to_target - my_to_target)

        # Slight preference for moves that don't increase distance to current target too much
        score += -0.05 * (cheb(sx, sy, tx, ty) - cheb(nx, ny, tx, ty) < 0)

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]