def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_xy(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict):
            if "position" in p:
                q = p["position"]
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    return int(q[0]), int(q[1])
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return None

    obs = set()
    for t in observation.get("obstacles", []) or []:
        q = to_xy(t)
        if q is not None:
            obs.add(q)

    res = []
    for t in observation.get("resources", []) or []:
        q = to_xy(t)
        if q is not None:
            res.append(q)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        return [0, 0]

    # Pick a resource where we are at least as close as opponent; else pick one that maximizes (opp_dist - self_dist)
    best_target = None
    best_key = None
    for rx, ry in res:
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        lead = opp_d - self_d
        tie = 1 if self_d <= opp_d else 0
        # Prefer: (self can beat opp), then larger lead, then smaller self distance, then deterministic by coord
        key = (tie, lead, -self_d, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    # Try move options; score by resulting nearest-resource race advantage
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Compute our and opp best race metrics to remaining resources after our step
        self_best = None
        opp_best = None
        for rx, ry in res:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # we want to minimize self distance for resources we can reach first, and maximize advantage
            tie = 1 if self_d <= opp_d else 0
            key_self = (tie, -self_d, rx, ry)
            if self_best is None or key_self > self_best:
                self_best = key_self
            key_opp = (-opp_d, rx, ry)
            if opp_best is None or key_opp > opp_best:
                opp_best = key_opp
        # Final move preference: maximize race tie, then maximize lead, then minimize our distance to chosen target, deterministic
        chosen_self_d = abs(tx - nx) + abs(ty - ny)
        chosen_opp_d = abs(tx - ox) + abs(ty - oy)
        lead = chosen_opp_d - chosen_self_d
        tie = 1 if chosen_self_d <= chosen_opp_d else 0
        move_key = (tie, lead, -chosen_self_d, dx, dy)
        if best_move_key is None or move_key > best_move_key:
            best_move_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]