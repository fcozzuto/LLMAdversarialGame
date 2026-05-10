def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [m for m in moves if -1 <= m[0] <= 1 and -1 <= m[1] <= 1]

    # Pick top few resources deterministically to keep evaluation cheap.
    ranked = []
    for r in res:
        sd = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        # Higher is better: contest advantage, closer to us (sd lower), and favor left/top for tie stability.
        key = (od - sd, -sd, -r[0], -r[1])
        ranked.append((key, r))
    ranked.sort(key=lambda x: x[0], reverse=True)
    candidates = [ranked[i][1] for i in range(min(4, len(ranked)))]

    best_m = (0, 0)
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        # Immediate pickup bonus if moving onto a resource.
        pickup = 1 if (nx, ny) in res else 0

        # Evaluate as: current best resource preference after the move, also penalize moves that let opponent get closer.
        best_local = None
        for r in candidates:
            nsd = cheb((nx, ny), r)
            nod = cheb((ox, oy), r)  # opponent position unchanged this turn
            # Encourage reducing our distance while keeping/expanding opponent's disadvantage.
            v = (nod - nsd, -nsd, -r[0], -r[1])
            if best_local is None or v > best_local:
                best_local = v
        # Slight preference for advancing (avoid pure oscillation): reward smaller distance to chosen top resource.
        top_r = candidates[0]
        adv = -cheb((nx, ny), top_r)

        # Combine; keep deterministic ordering by including (dx,dy) in tie-break.
        if best_v is None:
            best_v = (pickup, best_local, adv, -abs(dx) - abs(dy), -dx, -dy)
            best_m = (dx, dy)
        else:
            cand_v = (pickup, best_local, adv, -abs(dx) - abs(dy), -dx, -dy)
            if cand_v > best_v:
                best_v = cand_v
                best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]