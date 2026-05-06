def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Candidate resources: those either we can reach reasonably or opponent is already close to.
    scored = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        scored.append((min(sd, od) + 0.01 * max(sd, od), rx, ry, sd, od))
    scored.sort(key=lambda t: t[0])
    cands = scored[:min(6, len(scored))]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_val = None
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        val = 0.0
        # Denial-focused: if opponent is closer to a resource, prioritize reducing their lead.
        for _, rx, ry, sd0, od0 in cands:
            sd1 = man(nx, ny, rx, ry)
            od1 = man(ox, oy, rx, ry)
            lead0 = od0 - sd0
            lead1 = od1 - sd1
            # Encourage being closer or at least catching up; discourage letting them improve.
            progress = (lead0 - lead1)
            # Prefer nearer resources regardless, but keep denial pressure.
            base = (od1 - sd1) * 25 - sd1 - 0.002 * (rx + ry)
            # Small anti-oscillation: prefer moves that change position unless equal.
            pos_bias = 0.15 if (dx != 0 or dy != 0) else 0.0
            val += base + 8.0 * progress + pos_bias
        # Additional tie-break: avoid being trapped adjacent only by moving toward any resource direction.
        if val == best_val:
            if man(nx, ny, cands[0][1], cands[0][2]) < man(sx, sy, cands[0][1], cands[0][2]):
                best_val = val
                best_move = (dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]