def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

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

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    tx, ty = w // 2, h // 2

    if not resources:
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty)
            t = cheb(nx, ny, ox, oy)
            key = (v, -t, nx, ny)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return list(best[1]) if best else [0, 0]

    best_key = None
    best_move = (0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # For this next position, evaluate the best resource "lead" we can get.
        # Lead = (opponent distance to resource) - (self distance to resource)
        # Also mildly prefer moving into states that keep us closer than opponent to center.
        local_best = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd
            # If we can arrive sooner, prefer it; if tied, prefer resource that also denies opponent pressure
            # by increasing their distance.
            sec = -od + sd
            # Deterministic tie-break via coordinates.
            key = (lead, sec, -cheb(nx, ny, tx, ty), rx, ry)
            if local_best is None or key > local_best[0]:
                local_best = (key, sd)
        # Prefer next steps that maximize lead; if no lead, minimize own distance to nearest resource.
        own_min = local_best[1] if local_best else cheb(nx, ny, tx, ty)
        opp_near = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        key = (local_best[0][0], -own_min, -opp_near, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]