def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    ox, oy = observation["opponent_position"]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if oppT:
        sx = sy = 0
        for px, py in oppT:
            sx += px
            sy += py
        ocx = sx / len(oppT)
        ocy = sy / len(oppT)
    else:
        ocx, ocy = w - 1, h - 1

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (abs(p[0] - x) + abs(p[1] - y), p[0], p[1]))
    else:
        tx, ty = int(round(ocx)), int(round(ocy))

    def unclaimed_frontier(px, py):
        c = 0
        for ddx, ddy in dirs:
            nx2, ny2 = px + ddx, py + ddy
            if inb(nx2, ny2) and (nx2, ny2) in unclaimed:
                c += 1
        return c

    opp_dist = abs(x - ocx) + abs(y - ocy) + 1e-9
    self_adv = 1.0
    if observation.get("self_territory_count", 0) < observation.get("opponent_territory_count", 0):
        self_adv = 1.15

    best = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        d_to_target = abs(nx - tx) + abs(ny - ty)
        d_from_opp = abs(nx - ocx) + abs(ny - ocy)
        front = unclaimed_frontier(nx, ny)
        captures = 0
        if (nx, ny) in oppT:
            captures = 1
        # Deterministic combined heuristic
        score = (-2.2 * d_to_target) + (3.8 * front) + (0.9 * d_from_opp / opp_dist) * self_adv + (5.0 * captures)
        # Slight bias to keep moving out of self territory boundary if trailing
        if selfT and (x, y) in selfT:
            score += 0.3 * (1 if (nx, ny) not in selfT else -0.2)
        if score > best_score or (score == best_score and (dx, dy) < tuple(best)):
            best_score = score
            best = [dx, dy]

    if best == [0, 0]:
        return [0, 0]
    return best