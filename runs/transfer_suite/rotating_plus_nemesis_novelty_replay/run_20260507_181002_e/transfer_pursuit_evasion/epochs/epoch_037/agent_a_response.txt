def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evader" in sr) or ("runner" in sr)
    opp_is_evader = ("evader" in orr) or ("runner" in orr)

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def clamp_step(curx, cury, tx, ty):
        dx = 0 if tx == curx else (1 if tx > curx else -1)
        dy = 0 if ty == cury else (1 if ty > cury else -1)
        return dx, dy

    def choose_for(posx, posy, targetx, targety, wants_away):
        ddx, ddy = clamp_step(posx, posy, targetx, targety)
        # Prefer the direct step; then tie-break by best objective.
        preferred = []
        for dx, dy in moves:
            nx, ny = posx + dx, posy + dy
            if not free(nx, ny):
                continue
            if dx == ddx and dy == ddy:
                preferred.append((dx, dy))
        candidates = preferred if preferred else [(dx, dy) for dx, dy in moves if free(posx + dx, posy + dy)]
        best = None
        for dx, dy in candidates:
            nx, ny = posx + dx, posy + dy
            d = dist(nx, ny, targetx, targety)
            score = d if wants_away else -d
            # Deterministic tie-break: lexicographic by (dx,dy)
            key = (score, -nx, -ny, dx, dy)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Predict opponent next move using opponent's role (greedy).
    if opp_is_evader:
        opp_move = choose_for(ox, oy, sx, sy, True)
    else:
        # If opponent is pursuer, predict it trying to reduce distance to us.
        opp_move = choose_for(ox, oy, sx, sy, False)
    nox, noy = ox + opp_move[0], oy + opp_move[1]
    if not free(nox, noy):
        nox, noy = ox, oy

    if self_is_evader:
        targetx, targety = nox, noy
        wants_away = True
    else:
        # If we are pursuer, aim to reduce distance to predicted opponent position.
        targetx, targety = nox, noy
        wants_away = False

    dx, dy = choose_for(sx, sy, targetx, targety, wants_away)
    return [int(dx), int(dy)]