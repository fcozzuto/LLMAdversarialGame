def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or ("pursue" in role) or ("chaser" in role) or ("pursuit" in role)
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    bestv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = abs(nx - ox)
        e = abs(ny - oy)
        cheb = d if d > e else e
        if pursuer:
            val = -cheb * 1000 - (min(nx, ny, w - 1 - nx, h - 1 - ny) * 2)
        else:
            val = cheb * 1000 + (min(nx, ny, w - 1 - nx, h - 1 - ny) * 2)
        if bestv is None or val > bestv:
            bestv = val
            best = [dx, dy]
    if best is None:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return best