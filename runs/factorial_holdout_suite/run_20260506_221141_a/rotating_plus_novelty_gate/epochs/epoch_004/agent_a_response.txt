def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obstacles:
        x, y = p
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best_t = None
    for p in resources:
        x, y = int(p[0]), int(p[1])
        if not (0 <= x < w and 0 <= y < h) or (x, y) in obs_set:
            continue
        md = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        margin = od - md  # positive => we can arrive sooner
        cand = (0 if margin > 0 else 1, -margin, md, x, y)
        if best_t is None or cand < best_t[0]:
            best_t = (cand, (x, y))
    if best_t is None:
        return [0, 0]
    tx, ty = best_t[1]

    best_m = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs_set:
                continue
            tmd = cheb(nx, ny, tx, ty)
            tod = cheb(ox, oy, tx, ty)
            # Prefer improving capture race, then getting closer, then deterministic coord
            margin_next = tod - tmd
            score = (0 if margin_next > 0 else 1, -margin_next, tmd, nx, ny)
            if best_m is None or score < best_m[0]:
                best_m = (score, (dx, dy))
    if best_m is None:
        return [0, 0]
    return [int(best_m[1][0]), int(best_m[1][1])]