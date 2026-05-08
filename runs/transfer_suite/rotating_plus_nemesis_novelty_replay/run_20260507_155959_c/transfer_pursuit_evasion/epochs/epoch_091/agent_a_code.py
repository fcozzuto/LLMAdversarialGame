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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_evader = ("evad" in self_role) or ("runner" in self_role) or ("evasion" in self_role) or (self_role == "evader")
    opp_evader = ("evad" in opp_role) or ("runner" in opp_role) or ("evasion" in opp_role) or (opp_role == "evader")
    pursuing = (not self_evader) or opp_evader  # chase if we can, otherwise evade

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            cand.append(((-10**18), dx, dy))
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        # obstacle proximity penalty (discourage moving adjacent to obstacles when pursuing; less so when evading)
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs:
                    prox += 1
        # small tie-break toward "directionality"
        dirbias = -(dx * (1 if ox > sx else -1 if ox < sx else 0) + dy * (1 if oy > sy else -1 if oy < sy else 0))
        if pursuing:
            score = -dist2 - 0.7 * prox + 0.05 * dirbias
        else:
            score = dist2 - 0.3 * prox + 0.05 * (-dirbias)
        cand.append((score, dx, dy))

    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]