def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    obs = list(blocked)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        d0 = cheb(sx, sy, ox, oy)
        d1 = cheb(nx, ny, ox, oy)
        if is_evader:
            # Avoid stepping into "weak escape" areas near obstacles and don't drift toward pursuer.
            min_obs = 999
            for ax, ay in obs:
                t = cheb(nx, ny, ax, ay)
                if t < min_obs: min_obs = t
            # prefer larger distance, then prefer moving away vs current, then avoid near obstacles
            sc = (d1 * 1000) + ((d1 - d0) * 100) + (min_obs * 3)
        else:
            # Pursue while keeping distance from obstacles to avoid being boxed in.
            min_obs = 999
            for ax, ay in obs:
                t = cheb(nx, ny, ax, ay)
                if t < min_obs: min_obs = t
            sc = (-d1 * 1000) + (min_obs * 3) + ((d0 - d1) * 50)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best if best is not None else [0, 0]