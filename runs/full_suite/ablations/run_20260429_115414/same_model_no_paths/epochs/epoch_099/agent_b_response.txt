def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cd(ax, ay, bx, by):
        return abs(ax - bx) if abs(ax - bx) > abs(ay - by) else abs(ay - by)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose target: maximize opponent advantage in reaching it (own distance minimized)
    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cd(sx, sy, rx, ry)
        od = cd(ox, oy, rx, ry)
        key = (od - sd, -sd, -(rx + 13 * ry))  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_d = cd(ox, oy, rx, ry)

    # Pick move maximizing (opp_d - new_self_dist), with slight preference for staying closer to target
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        new_sd = cd(nx, ny, rx, ry)
        adv = opp_d - new_sd
        # If we can reach in one step, prioritize taking it.
        take = 1 if (nx == rx and ny == ry) else 0
        # Avoid moving toward boundaries if similarly scored.
        boundary_pen = (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1)
        score = (take, adv, -new_sd, -int(boundary_pen), -(dx * dx + dy * dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]