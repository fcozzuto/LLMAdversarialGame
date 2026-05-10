def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    us_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            us_moves.append((dx, dy))

    if not us_moves:
        return [0, 0]

    best_move = None
    best_score = None

    # One-step lookahead: assume opponent picks a move that maximizes distance from our resulting position.
    for dxu, dyu in us_moves:
        nxu, nyu = sx + dxu, sy + dyu
        opp_best_dist = None
        # deterministic tie-break: among best distance, choose lexicographically smallest (dx,dy) for opponent.
        opp_best_move = None
        for dxo, dyo in deltas:
            nxo, nyo = ox + dxo, oy + dyo
            if not inb(nxo, nyo):
                continue
            d = dist2(nxu, nyu, nxo, nyo)
            cand = (d, dxo, dyo)
            if opp_best_dist is None or cand[0] > opp_best_dist or (cand[0] == opp_best_dist and (dxo, dyo) < opp_best_move):
                opp_best_dist = cand[0]
                opp_best_move = (dxo, dyo)
        # minimize opponent's best achievable distance
        if best_score is None or opp_best_dist < best_score or (opp_best_dist == best_score and (dxu, dyu) < best_move):
            best_score = opp_best_dist
            best_move = (dxu, dyu)

    return [int(best_move[0]), int(best_move[1])]