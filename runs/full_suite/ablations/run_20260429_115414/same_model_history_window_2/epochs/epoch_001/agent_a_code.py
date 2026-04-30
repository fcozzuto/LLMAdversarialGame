def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0
        dy = 0
        return [dx, dy]
    def cheb(a, b, c, d):
        ax = a - c
        ay = b - d
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer / gain, then shorter for us
        key = (sd - od, sd, (rx + ry) & 7, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best
    def sign(v):
        return 0 if v == 0 else (-1 if v < 0 else 1)
    dx = sign(tx - sx)
    dy = sign(ty - sy)
    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    for nx, ny in candidates:
        nxp = sx + nx
        nyp = sy + ny
        if 0 <= nxp < w and 0 <= nyp < h and (nxp, nyp) not in obstacles:
            return [nx, ny]
    return [0, 0]