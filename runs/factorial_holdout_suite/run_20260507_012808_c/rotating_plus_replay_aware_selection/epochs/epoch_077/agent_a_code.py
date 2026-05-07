def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return max(abs(x2 - x1), abs(y2 - y1))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the resource where we are most ahead after this move.
        best_adv = -10**9
        best_self_d = 10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            adv = opp_d - self_d  # larger is better (we are closer than opponent)
            if self_d == 0:
                adv += 1000
            if adv > best_adv or (adv == best_adv and (self_d < best_self_d or (self_d == best_self_d and opp_d < best_opp_d))):
                best_adv = adv
                best_self_d = self_d
                best_opp_d = opp_d

        # Also penalize states where opponent is very close to any remaining resource.
        min_opp_any = 10**9
        for rx, ry in resources:
            od = dist(ox, oy, rx, ry)
            if od < min_opp_any:
                min_opp_any = od

        # Deterministic tie-breakers:
        # 1) maximize advantage, 2) minimize our distance to chosen resource, 3) maximize distance we keep from opponent,
        # 4) prefer moves that don't decrease Manhattan distance to the chosen resource too much.
        opp_keep = dist(nx, ny, ox, oy)
        md_self = abs(nx - ox) + abs(ny - oy)

        key = (best_adv, -best_self_d, -min_opp_any, opp_keep, -md_self)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]