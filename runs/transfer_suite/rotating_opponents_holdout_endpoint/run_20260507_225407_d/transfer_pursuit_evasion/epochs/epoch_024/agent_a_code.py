def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    is_pursuer = ("pursuer" in self_role) or ("pursuit" in self_role and "evasion" not in self_role) or ("pursue" in self_role)
    is_evader = ("evader" in self_role) or ("evasion" in self_role) or ("escape" in self_role)

    if not is_pursuer and not is_evader:
        is_pursuer = ("pursuer" in opp_role)  # if opponent pursuer, assume we are evader

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    d_now = abs(ox - sx) + abs(oy - sy)

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_next = abs(ox - nx) + abs(oy - ny)
        gain = d_now - d_next  # positive if moving closer
        # pursuer: maximize gain; evader: minimize gain
        primary = gain if is_pursuer else -gain
        # tie-breakers: avoid being captured (exact overlap), then prefer farther/closer accordingly, then stable preference order
        exact = 1 if (nx == ox and ny == oy) else 0
        dist_pref = -d_next if is_pursuer else d_next
        key = (primary, -exact, dist_pref, -abs(nx - sx) - abs(ny - sy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best