def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v, d=0):
        try:
            return int(v)
        except:
            return d

    sx, sy, ox, oy = ti(sx), ti(sy), ti(ox), ti(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    remaining = ti(observation.get("remaining_resource_count", len(resources)))

    # Target selection: secure when we can, otherwise deny harder via "tempo" (opp-self) plus proximity.
    best_t = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = ti(r[0]), ti(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        self_d = abs(tx - sx) + abs(ty - sy)
        opp_d = abs(tx - ox) + abs(ty - oy)

        # When resources are low, prioritize certainty (closest we can reach).
        if remaining <= 4:
            key = (-self_d, 0 if self_d <= opp_d else -1, opp_d)
        else:
            # If we can arrive no later, grab it quickly; else choose where we lose least "tempo".
            if self_d <= opp_d:
                key = (0, self_d, opp_d)
            else:
                key = (1, -(opp_d - self_d), self_d, opp_d)

        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t

    # Move selection with obstacle avoidance and deterministic tie-breaking.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_m_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Greedy toward target with slight preference to keep away from opponent (resource_denier).
        d_now = abs(tx - sx) + abs(ty - sy)
        d_next = abs(tx - nx) + abs(ty - ny)
        opp_now = abs(tx - ox) + abs(ty - oy)
        opp_next = abs(tx - ox) + abs(ty - oy)  # unchanged by our move

        my_progress = d_now - d_next
        opp_pressure = (opp_now - opp_next)  # always 0, but kept for structure
        opp_dist_from_me = abs(nx - ox) + abs(ny - oy)

        key = (my_progress, -d_next, -opp_dist_from_me, dx, dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]