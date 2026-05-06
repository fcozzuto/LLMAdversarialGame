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
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def resource_key(cx, cy):
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        return (od - sd, -sd, cx, cy)  # maximize advantage, then closer, deterministic

    if not resources:
        return [0, 0]

    cx, cy = max(resources, key=lambda r: resource_key(r[0], r[1]))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    opp_target = min(resources, key=lambda r: cheb(ox, oy, r[0], r[1]))
    itx, ity = opp_target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd_next = cheb(nx, ny, cx, cy)
        od_now = cheb(ox, oy, cx, cy)
        adv_next = od_now - sd_next

        # mild "interceptor": if opponent is extremely close to their nearest resource, drift toward it
        it_sd = cheb(nx, ny, itx, ity)
        opp_it_sd = cheb(ox, oy, itx, ity)
        intercept = -2 if opp_it_sd <= 1 else 0
        val = (adv_next, -sd_next + intercept, -it_sd, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move