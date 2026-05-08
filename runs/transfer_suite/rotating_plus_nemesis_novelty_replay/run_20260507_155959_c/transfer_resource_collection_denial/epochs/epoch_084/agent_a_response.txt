def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    env = observation.get("environment_name", "")

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (dx == 0 and dy == 0 or (nx, ny) not in obs):
                if dx != 0 or dy != 0:
                    if (nx, ny) not in obs:
                        moves.append((dx, dy))
                else:
                    moves.append((0, 0))
    if not moves:
        return [0, 0]

    if not resources:
        tx = (w - 1) if ox < w // 2 else 0
        ty = (h - 1) if oy < h // 2 else 0
        best = min(moves, key=lambda m: abs((sx + m[0]) - tx) + abs((sy + m[1]) - ty))
        return [best[0], best[1]]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    opp_t = (ox + (w - 1 - ox)) // 2
    center_bias = ((w - 1) / 2.0, (h - 1) / 2.0)

    def best_adv(nsx, nsy):
        my_best = -10**9
        opp_best = -10**9
        for rx, ry in resources:
            my_d = md(nsx, nsy, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # Advantage favors being closer; reward urgency; penalize giving opponent immediate access.
            adv = (opp_d - my_d) * 3 - my_d + (opp_d - my_d >= 0) * 2
            # Opponent's potential after our move (approx): how close they are to their best denial target.
            opp_pot = (my_d - opp_d) * 3 - opp_d
            if adv > my_best:
                my_best = adv
            if opp_pot > opp_best:
                opp_best = opp_pot
        # Slight preference to move toward board center to reduce dead-ends.
        cx, cy = center_bias
        center_term = -0.2 * (md(nsx, nsy, cx, cy) if isinstance(cx, int) else (abs(nsx - cx) + abs(nsy - cy)))
        # If opponent is very close to their preferred resource, prioritize denial (more strongly for resource_collection).
        deny_boost = 0
        if "resource_collection" in env:
            deny_boost = 1.0
        return my_best + center_term + deny_boost * (-opp_best * 0.05)

    # Deterministic tie-break: lexicographic on (dx,dy) after score
    scored = []
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        scored.append((best_adv(nsx, nsy), -abs((nsx - sx)) - abs((nsy - sy)), dx, dy))
    scored.sort(reverse=True)
    _, _, dx, dy = scored[0]
    return [int(dx), int(dy)]