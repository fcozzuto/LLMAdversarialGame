def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    pursuer = (not self_ev) or opp_ev

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        dist = cheb(nx, ny, ox, oy)
        center = abs(nx - cx) + abs(ny - cy)
        score = (dist, center) if pursuer else (-dist, -center)

        if best_val is None or score < best_val:
            best_val = score
            best_move = [dx, dy]
        elif best_val is not None:
            if score == best_val:
                # deterministic tie-break: prefer diagonal then cardinal then stay
                pref = - (abs(dx) + abs(dy))
                bpref = - (abs(best_move[0]) + abs(best_move[1]))
                if pref > bpref:
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]