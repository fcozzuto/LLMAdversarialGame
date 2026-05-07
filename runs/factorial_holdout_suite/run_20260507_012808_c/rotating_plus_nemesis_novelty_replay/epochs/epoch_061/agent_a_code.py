def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        for rx, ry in resources:
            d_self = manh(sx, sy, rx, ry)
            d_opp = manh(ox, oy, rx, ry)
            if d_self == 0:
                best = (0, d_self, d_opp, rx, ry)
                break
            # Prefer resources we can reach sooner; otherwise reduce our lead distance.
            lead = d_self - d_opp
            score = (lead, d_self, -d_opp, (rx + ry + ti) % 7, rx, ry)
            if best is None or score < best[:len(score)]:
                best = score
        tx, ty = best[-2], best[-1]

    # Choose best immediate move toward target; deterministic tie-break.
    best_move = (10**9, 0, 0)
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target.
        d = manh(nx, ny, tx, ty)
        # Secondary: if target contested, also slightly increase our distance from opponent.
        contest = 0 if not resources else manh(nx, ny, tx, ty) - manh(ox, oy, tx, ty)
        opp_sep = manh(nx, ny, ox, oy)
        # Micro tie-break: deterministic based on move and turn.
        tie = ((nx * 31 + ny * 17 + dx * 7 + dy * 13 + ti) % 11)
        cand = (d + 0.02 * contest - 0.005 * opp_sep + 0.001 * tie, d, -opp_sep, dx, dy)
        if cand < best_move:
            best_move = cand
    return [int(best_move[3]), int(best_move[4])]