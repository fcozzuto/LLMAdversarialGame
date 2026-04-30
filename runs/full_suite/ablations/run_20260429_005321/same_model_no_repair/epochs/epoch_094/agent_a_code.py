def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        c = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if (x + dx, y + dy) in obst:
                c += 1
        return c

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Target selection: prefer resources where we are (materially) closer than opponent.
    # If all are contested, fall back to minimizing our distance.
    best_move = None
    best_score = -10**18
    if resources:
        best_targets = []
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # margin >0 means we are closer; reward it, but penalize if too far for us soon
            best_targets.append((do - ds, -ds, rx, ry))
        best_targets.sort(reverse=True)
        # Use top few deterministically
        candidates = best_targets[:min(4, len(best_targets))]
    else:
        # No resources: move toward opponent side (diagonally biased) to deny space
        tx, ty = w - 1, h - 1
        candidates = [(0, 0, tx, ty)]

    for dx, dy, nx, ny in legal:
        move_score = 0
        move_score -= 0.6 * near_obst(nx, ny)
        # Evaluate against best resource targets
        if resources:
            local_best = -10**18
            for m, nsneg, rx, ry in candidates:
                ds2 = cheb(nx, ny, rx, ry)
                do2 = cheb(ox, oy, rx, ry)
                # immediate advantage term plus closeness after our move
                val = (do2 - ds2) * 2.2 - ds2 * 0.35
                if val > local_best:
                    local_best = val
            move_score += local_best
        else:
            # chase toward opponent corner while avoiding obstacles
            move_score += -cheb(nx, ny, w - 1, h - 1) * 0.9
        # Small deterministic tie-break to prefer "more forward" motion
        move_score += 0.01 * (dx - dy)

        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]
        elif move_score == best_score and best_move is not None:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move