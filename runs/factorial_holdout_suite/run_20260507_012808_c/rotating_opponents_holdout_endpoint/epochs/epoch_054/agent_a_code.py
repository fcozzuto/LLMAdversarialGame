def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18
    best_tie = 10**9

    # One-turn lookahead: pick move that maximizes our advantage to the best target
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles:
            continue

        local_best = -10**18
        local_best_ds = 10**9
        local_best_adv = -10**9
        # Evaluate each resource as possible next capture
        for rx, ry in resources:
            ds = dist_cheb(nx, ny, rx, ry)
            do = dist_cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer
            # Prefer winning resources; discourage targets where opponent is equally close
            sc = adv * 100 - ds * 2
            if adv < 0:
                sc -= 30 * (-adv)
            # If opponent can capture this immediately next turn (do == 1 and we're not at ds<=1), penalize
            if do <= 1 and ds > 1:
                sc -= 250
            # If we can capture immediately, strongly prefer
            if ds == 0:
                sc += 10000
            if sc > local_best or (sc == local_best and (ds < local_best_ds or (ds == local_best_ds and adv > local_best_adv))):
                local_best = sc
                local_best_ds = ds
                local_best_adv = adv

        # Additional deterministic nudge: avoid moves that bring us closer to opponent when we can't secure a win
        nud = 0
        if local_best_adv < 1:
            nud = -dist_cheb(nx, ny, ox, oy)

        total = local_best + nud
        tie = local_best_ds
        if total > best_score or (total == best_score and tie < best_tie):
            best_score = total
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]