def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [None, None])
    obs = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs if p and len(p) >= 2)
    selfT = observation.get("self_territory") or []
    oppT = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_set = set((p[0], p[1]) for p in selfT if p and len(p) >= 2)
    opp_set = set((p[0], p[1]) for p in oppT if p and len(p) >= 2)
    un_set = set((p[0], p[1]) for p in unclaimed if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_target = None
    best_key = None

    adj_to_self = []
    for (x, y) in un_set:
        if (x-1, y) in self_set or (x+1, y) in self_set or (x, y-1) in self_set or (x, y+1) in self_set:
            adj_to_self.append((x, y))

    candidates = adj_to_self if adj_to_self else list(un_set)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for (tx, ty) in candidates:
        d = abs(tx - sx) + abs(ty - sy)
        to_center = abs(tx - cx) + abs(ty - cy)
        opp_close = 0
        if ox is not None:
            opp_close = -(abs(tx - ox) + abs(ty - oy) <= 2)  # prefer not-too-close targets
        key = (d, to_center, opp_close, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = (best_target if best_target is not None else (int(round(cx)), int(round(cy))))
    best_move = None
    best_move_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_set and (nx, ny) not in self_set:
            continue
        d_new = abs(tx - nx) + abs(ty - ny)
        d_old = abs(tx - sx) + abs(ty - sy)
        step_gain = d_old - d_new
        key = (-step_gain, d_new, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    if best_move is not None:
        return best_move
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]