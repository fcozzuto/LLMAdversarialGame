def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    rem = observation.get("remaining_resource_count", len(resources))
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Heuristic: choose a move that maximizes "winning chances" on the best resource:
    # Prefer resources where we can arrive no later than opponent; else minimize our disadvantage.
    # Also apply a small penalty for moving near obstacles to avoid getting wedged.
    def obs_penalty(nx, ny):
        p = 0
        for bx, by in blocked:
            if cheb(nx, ny, bx, by) <= 1:
                p += 1
        return p

    best_score = -10**18
    best_move = (0, 0)

    if resources and rem > 0:
        for dx, dy, nx, ny in legal:
            myd = []
            for rx, ry in resources:
                if (rx, ry) in blocked:
                    continue
                d1 = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                # Winning margin: positive if we are closer or tied.
                margin = d2 - d1
                # If we are winning, prefer quicker wins; if losing, prefer reducing the gap.
                val = (1000 if margin >= 0 else 0) + margin * 5 - d1
                myd.append(val)
            if myd:
                score = max(myd) - 0.7 * obs_penalty(nx, ny)
            else:
                # Fallback: just move toward nearest unblocked resource with some opponent-aware bias.
                best = -10**18
                for rx, ry in resources:
                    if (rx, ry) in blocked:
                        continue
                    d1 = cheb(nx, ny, rx, ry)
                    d2 = cheb(ox, oy, rx, ry)
                    best = max(best, (d2 - d1) * 5 - d1)
                score = best - 0.7 * obs_penalty(nx, ny)
            # Deterministic tie-break: smallest dx, then dy, then lex by move
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)
    else:
        # No resources: move toward center to reduce being trapped; still avoid obstacles.
        cx, cy = w // 2, h // 2
        for dx, dy, nx, ny in legal:
            score = -cheb(nx, ny, cx, cy) - 0.7 * obs_penalty(nx, ny)
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]