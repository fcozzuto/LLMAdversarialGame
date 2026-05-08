def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = str(observation.get("self_role", "") or "")
    opp_role = str(observation.get("opponent_role", "") or "")
    rl = self_role.lower()
    ol = opp_role.lower()
    if "evader" in rl and "pursuer" in ol:
        role = "evader"
    elif "pursuer" in rl and "evader" in ol:
        role = "pursuer"
    else:
        scores = observation.get("scores", None)
        my_s, op_s = 0, 0
        if isinstance(scores, dict):
            my_s = scores.get("self", scores.get("me", scores.get("agent", 0))) or 0
            op_s = scores.get("opponent", scores.get("opp", scores.get("enemy", 0))) or 0
        elif isinstance(scores, (list, tuple)) and len(scores) >= 2:
            my_s, op_s = scores[0] or 0, scores[1] or 0
        role = "pursuer" if my_s <= op_s else "evader"

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if role == "evader":
        # New: commit to the farthest corner from pursuer (robust vs zigzags).
        target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        target = (ox, oy)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    # Deterministic tie-break: fixed iteration order of dx,dy.
    for dx, dy, nx, ny in moves:
        cur = (nx, ny)
        d_opp = man(cur, (ox, oy))
        d_tar = man(cur, target)
        d_now = man((sx, sy), (ox, oy))
        # Prefer movement that changes distance in our favor.
        if role == "pursuer":
            score = -d_opp + 0.02 * d_tar - 0.005 * (dx == 0 and dy == 0)
        else:
            score = d_opp + 0.02 * d_tar - 0.005 * (dx == 0 and dy == 0)
            # Extra: if we're not improving distance, prefer a move toward target corner.
            if d_opp <= d_now:
                score += 0.01 * (-d_tar)
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]