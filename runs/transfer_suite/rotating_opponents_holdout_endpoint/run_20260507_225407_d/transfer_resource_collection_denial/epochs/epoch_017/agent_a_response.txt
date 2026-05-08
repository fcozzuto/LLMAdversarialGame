def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles

    target_leads = []
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd < od:
            target_leads.append((od - sd, -sd, rx, ry))
    if target_leads:
        _, _, tx, ty = max(target_leads)
    else:
        _, tx, ty = min((cheb(sx, sy, rx, ry), rx, ry) for rx, ry in resources)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Primary: minimize distance to chosen target; Secondary: maximize separation from opponent.
        cand = (d_to, -d_opp, dx, dy)
        if best is None or cand < best:
            best = cand
    if best is None:
        return [0, 0]
    return [best[2], best[3]]