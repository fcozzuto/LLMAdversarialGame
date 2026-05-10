def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("pursuer" in opp_role) and ("evader" in self_role or "pursuit" in self_role))
    # fallback: if unsure, behave like evader (maximize distance) to match typical score setup

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def min_dist_to_resources(nx, ny):
        if not res:
            return None
        return min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_res = min_dist_to_resources(nx, ny)
        # Evader: maximize opp distance; also slightly prefer reducing distance to resources if present.
        # Pursuer: minimize opp distance; also slightly prefer reducing distance to resources if present.
        if is_evader:
            score = (d_opp, -d_res if d_res is not None else 0)
        else:
            score = (-d_opp, -d_res if d_res is not None else 0)
        if best is None or score > best[0] or (score == best[0] and (nx, ny) < best[1]):
            best = (score, (nx, ny), dx, dy)

    if best is None:
        return [0, 0]
    return [best[2], best[3]]