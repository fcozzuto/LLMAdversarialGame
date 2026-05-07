def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    env = observation.get("environment_name", "")
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                valid.append((x, y))

    if not valid:
        return [0, 0]

    best = None
    # Favor winning race; otherwise delay/deny earlier (especially vs resource_denier).
    for tx, ty in valid:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        if sd < od:
            score = (0, sd - od, sd, tx, ty)
        else:
            denom = 1 if env == "resource_collection" else 0
            score = (1, -(od - sd), (od if denom else 0), sd, tx, ty)
        if best is None or score < best[0]:
            best = (score, tx, ty)

    _, tx, ty = best
    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [mdx, mdy]
    return [0, 0]