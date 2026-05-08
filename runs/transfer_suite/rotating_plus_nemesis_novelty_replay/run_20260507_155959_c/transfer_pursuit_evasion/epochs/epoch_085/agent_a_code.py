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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or self_role == "evader"
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or opp_role == "evader"
    chase = not self_evader or opp_evader

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny)
        key = d if chase else -d
        if best_key is None or key < best_key or (key == best_key and (dx, dy) < best):
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]