def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Prefer resources where we can improve the "race"
    res_list = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        res_list.append((rx, ry, od - sd, sd, od))
    res_list.sort(key=lambda t: (-(t[2]), t[3], t[4]))
    targets = res_list[:6]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Compute move score by how well it improves race advantage vs opponent
        score = 0
        for rx, ry, race_gain, sd, od in targets:
            nsd = cheb(nx, ny, rx, ry)
            nod = od  # opponent distance unchanged this turn (no opponent move modeled)
            # primary: race swing
            score += (nod - nsd) * 12 - nsd
            # secondary: if we're already behind, prioritize moves that close the gap fast
            if nsd > nod:
                score += -3 * (nsd - nod)
            else:
                score += 6
            # tertiary: slight preference for targets closer to our next position
            score += -1 * (abs(nx - rx) + abs(ny - ry)) // 3
        # small deterministic tie-break: favor moves that keep us nearer board center
        center_bias = -(abs(nx - (gw - 1) / 2) + abs(ny - (gh - 1) / 2))
        score += center_bias * 0.01
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]