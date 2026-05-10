def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # If we are on a resource, take it (highest priority).
        on_resource = (nx, ny) in set(res)
        if on_resource:
            return [dx, dy]

        # Choose move that maximizes our best "grab" over opponent.
        best_adv = None
        best_my_d = None
        best_opp_d = None
        for rx, ry in res:
            my_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            adv = opp_d - my_d
            if (best_adv is None or adv > best_adv or
                (adv == best_adv and (my_d < best_my_d or (my_d == best_my_d and opp_d < best_opp_d)))):
                best_adv, best_my_d, best_opp_d = adv, my_d, opp_d

        # Lexicographic preference: maximize advantage; then minimize my distance; then maximize opp distance.
        score = (best_adv, -best_my_d, best_opp_d)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [best_move[0], best_move[1]]