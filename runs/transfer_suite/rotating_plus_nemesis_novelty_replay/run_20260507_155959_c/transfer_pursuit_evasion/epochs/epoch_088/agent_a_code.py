def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def sign(z):
        return 0 if z == 0 else (1 if z > 0 else -1)

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or (self_role == "evader") or ("escape" in self_role)
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or (opp_role == "evader") or ("escape" in opp_role)
    chase = (not self_evader) or opp_evader

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    tx, ty = sign(ox - sx), sign(oy - sy)
    base = []
    if chase:
        pref = [(tx, 0), (0, ty), (tx, ty)]
    else:
        pref = [(-tx, 0), (0, -ty), (-tx, -ty)]
    for a, b in pref:
        if a != 0:
            base.append((a, 0))
        if b != 0:
            base.append((0, b))
    base.extend([d for d in dirs if d not in base])
    candidates = base[:]

    best = None
    best_val = None
    turn = int(observation.get("turn_index") or 0)
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        val = dist if chase else -dist
        val += ((nx + ny + turn) % 2) * 1e-6
        if best is None or val < best_val if chase else val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]
    return [int(best[0]), int(best[1])]