def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            obs.add((b[0], b[1]))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        resources_scored = []
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                resources_scored.append((cheb(sx, sy, rx, ry), rx, ry))
        resources_scored.sort(key=lambda t: (t[0], t[1], t[2]))
        targets = [(t[1], t[2]) for t in resources_scored[:5]]
    else:
        targets = []

    if not targets:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    best = None
    for tx, ty in targets:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            # tie-break: also move slightly away from opponent if equally good
            od = cheb(nx, ny, ox, oy)
            key = (d, -od, nx, ny)
            if best is None or key < best[0]:
                best = (key, (dx, dy))

    if best is not None:
        return [best[1][0], best[1][1]]

    # fallback: any legal move, deterministic by direction order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]