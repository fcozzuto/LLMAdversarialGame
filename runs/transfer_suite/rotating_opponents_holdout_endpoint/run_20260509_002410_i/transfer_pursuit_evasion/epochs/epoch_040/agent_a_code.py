def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    is_evader = (self_role == "evader") or ("evader" in self_role) or (opponent_role == "pursuer")
    is_pursuer = (self_role == "pursuer") or ("pursuer" in self_role) or (opponent_role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # Prefer obstacle safety by penalizing being adjacent to obstacles.
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obstacles:
                    adj += 1
        # If tie-breaking, use deterministic preference order.
        pref = (dx, dy)

        if is_pursuer and not is_evader:
            # Minimize distance, strongly avoid adjacency.
            score = -d - 0.35 * adj
        else:
            # Evader: maximize distance, avoid adjacency.
            score = d - 0.35 * adj

        if best_score is None or score > best_score or (score == best_score and pref < best):
            best_score = score
            best = pref

    if best is None:
        return [0, 0]
    return [best[0], best[1]]