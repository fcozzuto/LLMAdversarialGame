def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Choose a resource that maximizes our potential to be the first (opp closer than us)
    # with a secondary preference for being near and avoiding far travel.
    best_t = None
    best_k = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        k = (od - sd, -sd, -tx, -ty)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (tx, ty)
    tx, ty = best_t

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            # Evaluate how well this move contests the chosen resource
            our_d_after = cheb(nx, ny, tx, ty)
            opp_d_now = cheb(ox, oy, tx, ty)
            contest = opp_d_now - our_d_after
            # Prefer progress and disfavor staying still unless forced
            moved = 1 if (dx != 0 or dy != 0) else 0
            closer_now = cheb(sx, sy, tx, ty) - our_d_after
            # Deterministic tie-breakers by direction and coordinate
            tie = (moved, closer_now, -abs(dx), -abs(dy), -nx, -ny)
            score = (contest, closer_now, moved, -our_d_after, tie)
            candidates.append((score, dx, dy))

    if not candidates:
        # If all candidate steps are blocked, try a bounded direct approach ignoring obstacles
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    our_d_after = cheb(nx, ny, tx, ty)
                    opp_d_now = cheb(ox, oy, tx, ty)
                    score = (opp_d_now - our_d_after, -our_d_after, dx, dy)
                    candidates.append((score, dx, dy))
    candidates.sort(reverse=True, key=lambda z: z[0])
    return [int(candidates[0][1]), int(candidates[0][2])]