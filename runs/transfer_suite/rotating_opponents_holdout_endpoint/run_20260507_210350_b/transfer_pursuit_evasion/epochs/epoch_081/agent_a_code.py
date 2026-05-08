def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_pursuer = ("pursuer" in role) or (role == "pursuer") or (("evader" in opp_role) and ("pursuer" not in role))
    # If still unclear, default to pursue if name suggests
    if role == "" and opp_role == "":
        is_pursuer = True

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    prefer = corners[phase]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        # Base objective: pursuer minimize manhattan distance, evader maximize
        d = abs(nx - ox) + abs(ny - oy)
        target_corner = prefer
        # Additional shaping: keep/approach preferred corner depending on role
        dc = abs(nx - target_corner[0]) + abs(ny - target_corner[1])
        value = -d if is_pursuer else d
        value += (-0.05 * dc) if is_pursuer else (-0.01 * dc)  # evader slightly favors corners too
        # If far from opponent, pursuer prioritizes getting closer; evader prioritizes maximizing distance
        if (d > (w + h) // 4) != is_pursuer:
            value += (0.02 * d) if is_pursuer else (0.02 * d)
        if bestv is None or (value > bestv if not is_pursuer else value > bestv):
            bestv = value
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]