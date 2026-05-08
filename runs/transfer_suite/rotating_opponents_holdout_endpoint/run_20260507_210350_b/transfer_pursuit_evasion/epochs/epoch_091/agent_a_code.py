def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    role = observation.get("self_role", "pursuer")
    if role not in ("pursuer", "evader"):
        role = "pursuer"

    target = (ox, oy)
    bestd = 10**9
    resources = observation.get("resources") or []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                d = abs(rx - sx) + abs(ry - sy)
                if d < bestd:
                    bestd = d
                    target = (rx, ry)

    tx, ty = target
    best_move = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_to_t = abs(tx - nx) + abs(ty - ny)
        dist_from_o = abs(ox - nx) + abs(oy - ny)
        score = -dist_to_t
        if role == "evader":
            score += 0.6 * dist_from_o
        else:
            score += 0.15 * dist_from_o
        if best_move is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best_move