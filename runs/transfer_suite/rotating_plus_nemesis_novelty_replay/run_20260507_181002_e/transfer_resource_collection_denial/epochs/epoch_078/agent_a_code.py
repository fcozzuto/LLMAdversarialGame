def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer grabbing/being closer to a resource; also try to deny by maximizing advantage.
    # Advantage for a resource: (opp_dist - self_dist). Larger is better.
    best = None
    for dx, dy, nx, ny in legal:
        worst_case = 10**9
        best_res_adv = -10**9
        closest_self = 10**9
        closest_opp = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_res_adv:
                best_res_adv = adv
            if sd < closest_self:
                closest_self = sd
            if od < closest_opp:
                closest_opp = od
            if sd == 0:
                best_res_adv = 10**9  # immediate pick
        # Small shaping: prefer moves that reduce self distance to the best target,
        # and slightly increase distance from the opponent when we can't win immediately.
        score = (best_res_adv * 1000) - (closest_self * 3) + (closest_opp * 1)
        # Deterministic tie-break: smaller dx, then smaller dy, then prefer staying still.
        cand = (score, -1 if dx == 0 and dy == 0 else 0, -dx, -dy, dx, dy)
        if best is None or cand > best[0]:
            best = (cand, [dx, dy])

    return best[1]