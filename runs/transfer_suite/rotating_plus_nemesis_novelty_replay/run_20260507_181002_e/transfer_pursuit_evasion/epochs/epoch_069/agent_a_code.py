def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("seeker" in sr)
    opp_is_pursuer = ("pursuer" in orr) or ("chaser" in orr) or ("seeker" in orr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score_pos(px, py, tx, ty, is_purs):
        d2 = (px - tx) * (px - tx) + (py - ty) * (py - ty)
        return -d2 if is_purs else d2

    def opp_best_move(ex, ey, tx, ty, opp_purs):
        # Opponent moves to minimize distance if pursuer, maximize if evader.
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = ex + dx, ey + dy
            if not legal(nx, ny):
                continue
            v = score_pos(nx, ny, tx, ty, opp_purs)
            if best is None or v > bestv:
                best, bestv = (dx, dy), v
        return best if best is not None else (0, 0)

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if not legal(nsx, nsy):
            continue

        if ox == nsx and oy == nsy:
            return [dx, dy]

        # One-ply lookahead with opponent greedy response.
        opp_dx, opp_dy = opp_best_move(ox, oy, nsx, nsy, opp_is_pursuer)
        nos_ox, nos_oy = ox + opp_dx, oy + opp_dy

        # Evaluate after both moves from our perspective: pursuer wants decrease dist to opponent;
        # evader wants increase dist.
        our_purs = self_is_pursuer
        val = score_pos(nsx, nsy, nos_ox, nos_oy, our_purs)

        # Tie-break: prefer capturing or staying closer/farther consistently; then deterministic order.
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]