def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, dict):
            x = o.get("x", o.get("px", o.get("pos_x", None)))
            y = o.get("y", o.get("py", o.get("pos_y", None)))
        else:
            try:
                x, y = o
            except Exception:
                continue
        if x is not None and y is not None:
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                obs.add((int(x), int(y)))
    res = observation.get("resources", []) or []
    rpos = []
    for r in res:
        if isinstance(r, dict):
            x = r.get("x", r.get("px", r.get("pos_x", None)))
            y = r.get("y", r.get("py", r.get("pos_y", None)))
        else:
            try:
                x, y = r
            except Exception:
                continue
        if x is not None and y is not None:
            rpos.append((int(x), int(y)))
    def dsq(a, b, c, d):
        dx = a - c; dy = b - d
        return dx*dx + dy*dy

    def best_escape():
        best = [0, 0]; bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs: continue
            v = dsq(nx, ny, ox, oy)
            if rpos:
                cx, cy = rpos[0]
                v += 0.02 * (-dsq(nx, ny, cx, cy))
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    if rpos:
        best = [0, 0]; bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs: continue
            md = min(dsq(nx, ny, rx, ry) for rx, ry in rpos)
            v = -md
            v += 0.1 * dsq(nx, ny, ox, oy)
            # small bias toward staying inside
            v += -0.001 * (abs(nx - w/2) + abs(ny - h/2))
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best
    return best_escape()