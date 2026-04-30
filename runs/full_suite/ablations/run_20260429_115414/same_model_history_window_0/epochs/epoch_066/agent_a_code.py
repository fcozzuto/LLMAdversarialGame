def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v
    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    if not resources:
        tx, ty = 0, 0
    else:
        best = None
        for rx, ry in resources:
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            val = od - sd  # positive means we're closer
            if best is None or val > best[0] or (val == best[0] and (sd < best[2] or (sd == best[2] and (rx+ry < best[3])))):
                best = (val, (rx, ry), sd, rx+ry)
        tx, ty = best[1]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    candidates = []
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # prefer moving closer to target; if tie, prefer reducing opponent distance
        d1 = dist((nx, ny), (tx, ty))
        d2 = dist((nx, ny), (ox, oy))
        candidates.append((d1, -d2, -abs(tx-nx)-abs(ty-ny), mx, my))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][3]), int(candidates[0][4])]