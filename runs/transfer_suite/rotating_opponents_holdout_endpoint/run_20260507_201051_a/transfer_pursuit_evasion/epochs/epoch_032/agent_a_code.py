def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    i_am_evader = ("evader" in self_role) or ("pursuer" in opponent_role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    def step_ok(x, y):
        return (x, y) not in obs

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    best = None
    best_score = None
    # Deterministic tie-break preference order: smaller dx, then smaller dy, then earlier in list.
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if not step_ok(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        # If pursuer: strongly prefer decreasing distance; if evader: prefer increasing distance.
        if i_am_evader:
            # Also avoid stepping into positions that let pursuer immediately get closer.
            # Evaluate one-step pursuer response toward us.
            relx, rely = nx - ox, ny - oy
            sxp, syp = (0 if relx == 0 else (1 if relx > 0 else -1)), (0 if rely == 0 else (1 if rely > 0 else -1))
            tx, ty = ox + sxp, oy + syp
            tx, ty = clamp(tx, ty)
            if not step_ok(tx, ty):
                # If blocked, assume pursuer can't improve much from that direction.
                pursuer_d2 = d2
            else:
                pursuer_d2 = dist2(nx, ny, tx, ty)
            score = (d2 * 10) - (pursuer_d2 * 3)
        else:
            # Pursuer prefers minimal distance; add obstacle penalty for being stuck.
            # If move is into immediate contact (distance 0), win will occur; prioritize heavily.
            score = -d2 * 10
            # Slightly favor moves that also reduce opponent's mobility by approaching around obstacles.
            around = 0
            for adx, ady in moves:
                ax, ay = clamp(nx + adx, ny + ady)
                if (ax, ay) in obs:
                    around += 1
            score += around * 0.5

        # Deterministic tie-break
        key = (score, -abs(dx), -abs(dy), moves.index((dx, dy)))
        if best is None or key > best_score:
            best = (dx, dy)
            best_score = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]