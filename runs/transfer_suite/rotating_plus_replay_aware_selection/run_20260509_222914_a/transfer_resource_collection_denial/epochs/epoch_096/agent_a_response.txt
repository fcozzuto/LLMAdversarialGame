def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_score = None
    best_t = (sx, sy)

    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        dist_term = (ds + 0.05)  # prefer nearer
        adv = do - ds           # positive means we are closer
        tie = (rx * 3 + ry)     # deterministic tie-break
        # Favor resources we can win; otherwise contest those we can deny.
        score = (adv * 10.0) - dist_term + (0.001 * tie)
        if best_score is None or score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    # Move greedily toward target while avoiding obstacles; deterministic tie-break by dirs order.
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            if cheb(nx, ny, tx, ty) < cheb(sx, sy, tx, ty):
                return [dxm, dym]

    # If cannot get closer, try any safe step that best improves opponent denial: minimize opp_cheb.
    best_step = [0, 0]
    best_opp = None
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            opp_d = cheb(ox, oy, nx, ny)
            self_d = cheb(nx, ny, tx, ty)
            k = (self_d, -opp_d)
            if best_opp is None or k < best_opp:
                best_opp = k
                best_step = [dxm, dym]
    return best_step