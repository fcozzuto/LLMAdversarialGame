def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

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

    def move_val(nx, ny, tx, ty):
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        return (od - sd, -sd, -tx, -ty)

    # pick a promising target deterministically
    best_t = None
    best_k = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        k = (od - sd, -sd, -cx, -cy)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (cx, cy)
    tx, ty = best_t

    best_m = None
    best_mk = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            # encourage getting the chosen target, and if multiple targets exist, also avoid letting opponent win others
            primary = move_val(nx, ny, tx, ty)
            opp_to_target_now = cheb(ox, oy, tx, ty)
            our_to_target_now = cheb(sx, sy, tx, ty)
            progress = 1 if cheb(nx, ny, tx, ty) < our_to_target_now else 0
            # small penalty if we move away from opponent (prevents risky drift on empty lines)
            den = -cheb(nx, ny, ox, oy)
            mk = (primary, progress, -abs(cheb(nx, ny, ox, oy) - opp_to_target_now), den, dx, dy)
            if best_mk is None or mk > best_mk:
                best_mk = mk
                best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]