def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_role = observation.get("self_role", "") or ""
    if not is_evader(self_role):
        srn = observation.get("self_role_name", "") or ""
        if is_evader(srn):
            self_role = srn
    if not is_evader(self_role):
        rr = observation.get("role", "") or ""
        if is_evader(rr):
            self_role = rr
    evading = is_evader(self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None
    # For evader: maximize distance; pursuer: minimize distance
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny)
        # prefer moving (not just tie-breaking) and avoid positions adjacent to obstacles
        near_obs = 0
        for ax, ay in obstacles:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                near_obs += 1
        score = d - (2.0 if evading else 0.0) * near_obs
        if best is None:
            best, best_score = (dx, dy), score
        else:
            better = score > best_score if evading else score < best_score
            if better:
                best, best_score = (dx, dy), score
            elif score == best_score and (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        # all blocked; stay put deterministically
        return [0, 0]
    return [int(best[0]), int(best[1])]