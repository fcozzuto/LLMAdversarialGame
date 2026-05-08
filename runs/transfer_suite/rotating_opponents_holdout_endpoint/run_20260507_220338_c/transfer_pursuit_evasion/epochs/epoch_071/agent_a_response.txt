def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("runner" in role_s) or ("flee" in role_s) or ("avoid" in role_s) or ("escape" in role_s)
    is_pursuer = ("pursuer" in role_s) or ("chaser" in role_s) or ("catch" in role_s) or ("hunter" in role_s) or ("pursuit" in role_s)
    if not is_pursuer and is_evader:
        pursue = False
    elif is_pursuer and not is_evader:
        pursue = True
    else:
        pursue = True  # default: pursuer in pursuit_evasion

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def score(nx, ny):
        d = max(abs(nx - ox), abs(ny - oy))  # chebyshev
        return -d if pursue else d

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        sc = score(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = (dx, dy)
        elif sc == best:
            # deterministic tie-break: prefer closer in intended direction; then lexicographic
            if pursue:
                dirx = (1 if ox > sx else -1 if ox < sx else 0)
                diry = (1 if oy > sy else -1 if oy < sy else 0)
            else:
                dirx = (-1 if ox > sx else 1 if ox < sx else 0)
                diry = (-1 if oy > sy else 1 if oy < sy else 0)
            curr = (dx * dirx + dy * diry)
            bm = best_move[0] * dirx + best_move[1] * diry
            if curr > bm or (curr == bm and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]