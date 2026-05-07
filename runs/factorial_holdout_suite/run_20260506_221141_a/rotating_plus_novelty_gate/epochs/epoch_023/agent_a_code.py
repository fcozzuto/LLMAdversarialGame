def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def dist_cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Choose target resource
    best = None
    best_key = None
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
            continue
        ds = dist_cheb(sx, sy, tx, ty)
        do = dist_cheb(ox, oy, tx, ty)
        key = (do - ds, -ds, -((tx + ty) & 1), -((tx * 31 + ty) & 1023), tx, ty)
        if best_key is None or key > best_key:
            best_key, best = key, (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy local move toward target while avoiding obstacles
    best_d = [0, 0]
    best_md = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            md = dist_cheb(nx, ny, tx, ty)
            # Prefer moves that also reduce opponent's chance on the same target
            ndopp = dist_cheb(ox, oy, tx, ty)
            key = (-(ndopp - md), -md, -((nx + ny) & 1), dx, dy)
            if best_md is None or key > best_md:
                best_md = key
                best_d = [dx, dy]

    return best_d