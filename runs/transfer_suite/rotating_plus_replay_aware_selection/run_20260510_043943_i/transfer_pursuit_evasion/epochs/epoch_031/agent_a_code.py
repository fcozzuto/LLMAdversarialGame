def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "guard", "pursuit")) or ("evader" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def corner_bias(x, y):
        # slight preference to keep us mobile: avoid being trapped near obstacles by minimizing surrounding blockage
        block = 0
        for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + ddx, y + ddy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                block += 1
        return block

    # 1-ply minimax: opponent moves deterministically to optimize its distance objective
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not valid(nsx, nsy):
            nsx, nsy = sx, sy  # engine keeps in place on invalid move
        # enumerate opponent response
        opp_best = None
        opp_target_dist = None
        for odx, ody in moves:
            nox, noy = ox + odx, oy + ody
            if not valid(nox, noy):
                nox, noy = ox, oy
            d = dist2(nsx, nsy, nox, noy)
            # if we are pursuer, opponent tries to maximize distance; else opponent tries to minimize distance
            if is_pursuer:
                val = d
                better = opp_best is None or val > opp_best
            else:
                val = -d
                better = opp_best is None or val > opp_best
            if better:
                opp_best = val
                opp_target_dist = d
        # our objective: if pursuer minimize distance, if evader maximize distance
        if is_pursuer:
            score = opp_target_dist
            if best_score is None or score < best_score or (score == best_score and corner_bias(nsx, nsy) < corner_bias(sx, sy)):
                best_score = score
                best_move = [dx, dy]
        else:
            score = opp_target_dist
            if best_score is None or score > best_score or (score == best_score and corner_bias(nsx, nsy) > corner_bias(sx, sy)):
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]