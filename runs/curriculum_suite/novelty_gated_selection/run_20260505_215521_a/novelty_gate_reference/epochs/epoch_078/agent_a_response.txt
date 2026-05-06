def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    nbrs = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                nbrs.append((dx, dy, nx, ny))

    res_set = set(resources)
    opp_before = cheb(ox, oy, sx, sy)

    best_move = (0, 0)
    best_val = None
    top = 6 if len(resources) > 6 else len(resources)

    for dx, dy, nx, ny in nbrs:
        val = 0
        if (nx, ny) in res_set:
            val += 2000
        if cheb(nx, ny, ox, oy) <= opp_before:
            val += 5  # keep contest closer in case opponent is aggressive
        # consider only a few closest resources to reduce brittleness
        dists = []
        for tx, ty in resources:
            dists.append((cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), tx, ty))
        dists.sort(key=lambda t: t[0])
        dists = dists[:top]

        # maximize being first to valuable near targets
        for sd, od, tx, ty in dists:
            if sd == 0:
                continue
            lead = od - sd  # positive if we reach sooner (in cheb metric)
            # prefer targets we can beat and that are close
            val += (lead * 60) - (sd * 10)
            # small bias to prevent drifting into corners away from resources
            val += -abs(tx - nx) * 1 - abs(ty - ny) * 1

        # tie-break: don't move farther from the currently closest resource
        cur_best = min(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))
        if cheb(nx, ny, cur_best[0], cur_best[1]) < cheb(sx, sy, cur_best[0], cur_best[1]):
            val += 3

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]