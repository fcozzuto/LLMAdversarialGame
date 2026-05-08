def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = observation.get("resources", []) or []
    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # Threat-first contest: prioritize resources the opponent is currently closest to.
    # Then pick moves that maximize chance to arrive first (or reduce opponent lead).
    opp_list = sorted(((md(ox, oy, rx, ry), rx, ry) for rx, ry in res), key=lambda t: (t[0], t[1], t[2]))
    topk = 6 if len(opp_list) >= 6 else len(opp_list)
    threats = opp_list[:topk]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = 0
        for d_op, rx, ry in threats:
            d_self = md(nx, ny, rx, ry)
            lead = d_op - d_self  # positive => we are closer than opponent for this resource
            if d_self <= d_op:
                score += (lead + 1) * 10  # strong preference for contests we can win now
            else:
                # If we can't win this contest, at least reduce their lead.
                score -= (abs(lead) + 1) * 3
            # Small preference to actually move toward the threat resource region.
            score -= d_self
        # Deterministic tie-break: prefer staying still if equally good, else prefer lexicographically smaller move.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]