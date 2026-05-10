def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    our_best = None
    opp_threat = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd
        t_our = (lead, -sd, rx + ry)
        t_opp = (-lead, sd, rx + ry)  # pick most negative lead (opponent ahead), tie toward larger sd
        if our_best is None or t_our > our_best[0]:
            our_best = (t_our, rx, ry, lead)
        if opp_threat is None or t_opp > opp_threat[0]:
            opp_threat = (t_opp, rx, ry, lead)

    _, tx, ty, our_lead = our_best
    _, ix, iy, threat_lead = opp_threat  # threat_lead = od - sd for opponent-ahead target
    intercept_mode = (our_lead < 0) or (threat_lead <= -1)

    target_x, target_y = (ix, iy) if intercept_mode else (tx, ty)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_val = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        sd_new = cheb(nx, ny, target_x, target_y)
        od_new = cheb(ox, oy, target_x, target_y)
        val = (od_new - sd_new) * 2 - sd_new
        if intercept_mode:
            val += -cheb(nx, ny, ox, oy) * 0.6
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move