def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if i_am_evader:
        target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        target_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = (None, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_tar = dist2(nx, ny, target_corner[0], target_corner[1])

        # Deterministic composite objective
        # Evader: maximize separation + also lean to (favorable) corner.
        # Pursuer: minimize separation (greedy tagger behavior) + slight bias toward corner.
        if i_am_evader:
            score = d_opp + 0.15 * d_tar
        else:
            score = -d_opp - 0.05 * d_tar

        # Small deterministic tie-breaker on step alignment toward/away from opponent and parity
        parity_bias = 0.001 * ((nx + ny) - (sx + sy))
        opp_align = (dx * (ox - sx) + dy * (oy - sy))
        if i_am_evader:
            score += -0.001 * opp_align + parity_bias
        else:
            score += 0.001 * opp_align + parity_bias

        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]