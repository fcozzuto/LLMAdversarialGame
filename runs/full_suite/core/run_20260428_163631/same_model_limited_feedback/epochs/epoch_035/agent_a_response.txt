def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obs_set = set()
    for p in obstacles:
        obs_set.add((p[0], p[1]))
    def clamp(a, lo, hi):
        if a < lo: return lo
        if a > hi: return hi
        return a
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # pick target resource: prefer those closer than opponent (larger distance advantage), then closer to self, then deterministic tie-break
    best = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obs_set:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # advantage first, then self distance, then lexicographic tie-break
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        # fallback: go toward center
        tx, ty = w//2, h//2
    else:
        tx, ty = best
    # desired direction toward target
    ddx = 0 if tx == sx else (1 if tx > sx else -1)
    ddy = 0 if ty == sy else (1 if ty > sy else -1)
    preferred = (ddx, ddy)
    # evaluate candidate moves deterministically: prefer preferred, then minimal distance to target, then avoid staying if possible
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        dist2 = abs(tx - sx) + abs(ty - sy)
        # keys: preferred first, then smaller distance to target, then lexicographic
        pref = 1 if (dx, dy) == preferred else 0
        cand.append((pref, -dist, -dist2 == 0, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [cand[0][3], cand[0][4]]