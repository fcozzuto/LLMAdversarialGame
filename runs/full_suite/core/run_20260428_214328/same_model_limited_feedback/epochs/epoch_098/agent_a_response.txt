def choose_move(observation):
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs_set = set((x, y) for x, y in obstacles)
    inb = lambda x, y: 0 <= x < gw and 0 <= y < gh

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            v = max(abs(nx - ox), abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose resource by relative closeness (I closer => negative advantage).
    best_res = None
    best_key = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (md - od, md, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    rx, ry = best_res
    my_adv = best_key[0]

    # If I'm not advantaged, avoid feeding: prefer resources where opponent is relatively far.
    if my_adv > 0:
        alt_res = None
        alt_key = None
        for ax, ay in resources:
            md = cheb(sx, sy, ax, ay)
            od = cheb(ox, oy, ax, ay)
            # maximize opponent distance relative to mine => larger (od - md)
            key = (- (od - md), md, ax, ay)
            if alt_key is None or key < alt_key:
                alt_key = key
                alt_res = (ax, ay)
        rx, ry = alt_res

    # Move greedily toward chosen target, with opponent-distance tie-break.
    best = (0, 0)
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_to = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer smaller distance to target; if close tie, prefer farther from opponent.
        key = (d_to, -d_opp, dx, dy)
        if bestv is None or key < bestv:
            bestv = key
            best = (dx, dy)

    if best == (0, 0):
        # If blocked, try any legal move that maximizes distance from opponent.
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_opp = cheb(nx, ny, ox, oy)
            if d_opp > bestv:
                bestv = d_opp
                best = (dx, dy)
    return [best[0], best[1]]