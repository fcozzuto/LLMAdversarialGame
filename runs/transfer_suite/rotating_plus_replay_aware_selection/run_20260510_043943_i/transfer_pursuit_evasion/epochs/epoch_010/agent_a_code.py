def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    role = observation.get("self_role", "pursuer")
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    vxo, vyo = sx - ox, sy - oy
    best = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if role == "pursuer":
            score = -d
            # small preference to reduce distance quickly and not get stuck
            if dx == 0 and dy == 0:
                score -= 1e-3
            # discourage illegal movement-equivalent stalling
            if (vxo == 0 and dx != 0) or (vyo == 0 and dy != 0):
                score += 1e-6
        else:
            score = d
            if dx == 0 and dy == 0:
                score -= 1e-3
            # orbit preference: move roughly perpendicular to pursuer-self vector when close
            if d <= 16:
                perp = abs(dx * vyo - dy * vxo)
                score += 0.01 * perp
        if bestscore is None or score > bestscore:
            bestscore = score
            best = [dx, dy]
        elif score == bestscore and best is not None:
            # deterministic tie-break: lexicographic on dx, then dy, preferring movement toward x first
            if (dx, dy) < (best[0], best[1]):
                best = [dx, dy]
    if best is None:
        return [0, 0]
    return best