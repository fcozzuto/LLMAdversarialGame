def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid_moves.append((dx, dy, nx, ny))
    if not valid_moves:
        return [0, 0]

    ox, oy = int(ox), int(oy)
    best = (0, 0)
    best_val = None

    # Prefer resources we can reach sooner; break ties by closer distance and better "blocking" (not letting opponent get immediate gain).
    # Deterministic: fixed iteration order and deterministic scoring.
    for dx, dy, nx, ny in valid_moves:
        best_for_move = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Advantage: positive if we are closer.
            adv = do - ds
            # If opponent is closer, discourage; still consider if we can become closer next step.
            # Small secondary terms encourage shortest path and away from giving opponent a "free" step toward same resource.
            opp_next = cheb(ox, oy, rx, ry)  # keep deterministic and cheap
            val = adv * 100 - ds * 3 - (0 if adv > 0 else 10) - (opp_next * 0)
            # If we currently can capture (adv>0), reward strongly by exact reachability window.
            if adv == 0:
                val -= 5
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        if best_val is None or best_for_move > best_val:
            best_val = best_for_move
            best = (dx, dy)
    return [int(best[0]), int(best[1])]