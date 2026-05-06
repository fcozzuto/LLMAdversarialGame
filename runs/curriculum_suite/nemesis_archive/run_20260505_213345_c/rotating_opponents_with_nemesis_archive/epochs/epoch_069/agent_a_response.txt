def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist8(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_step(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (dx, dy) == (0, 0) or (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles):
            return dx, dy
        # fallback: try axis-first (still deterministic)
        for adx, ady in [(dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]:
            nx, ny = sx + adx, sy + ady
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return adx, ady
        return 0, 0

    my_best = None
    best_val = None
    my_dists = []
    for (rx, ry) in resources:
        md = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        val = (od - md) * 10 - md  # prefer stealing (opp lead) then closer
        if best_val is None or val > best_val or (val == best_val and (md < my_dists[0] if my_dists else True)):
            my_best = (rx, ry)
            best_val = val
    # If opponent is extremely close to our chosen target, switch to one where we have lead
    tx, ty = my_best
    md0 = dist8(sx, sy, tx, ty)
    od0 = dist8(ox, oy, tx, ty)
    if od0 <= md0 + 1:
        lead_best = None
        lead_val = None
        for (rx, ry) in resources:
            md = dist8(sx, sy, rx, ry)
            od = dist8(ox, oy, rx, ry)
            lead = (md <= od)  # only take where we can be no slower
            val = (od - md) * 10 - md if lead else -10**9
            if lead_val is None or val > lead_val or (val == lead_val and (rx, ry) < (lead_best[0], lead_best[1])):
                lead_best = (rx, ry)
                lead_val = val
        if lead_best is not None:
            tx, ty = lead_best

    dx, dy = best_step(tx, ty)
    return [int(dx), int(dy)]