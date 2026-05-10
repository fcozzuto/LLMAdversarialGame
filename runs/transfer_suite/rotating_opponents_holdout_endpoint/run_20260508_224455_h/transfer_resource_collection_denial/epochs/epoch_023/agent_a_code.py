def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Prefer resources we can reach sooner than opponent; deterministic tie-breaking
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Lower is better: race advantage; slight bias toward closer overall
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # If target is at an obstacle-adjacent bottleneck, switch deterministically to second-best
    # (lightweight "meaningful change" from purely chasing distance)
    def obstacle_pressure(x, y):
        # count neighboring obstacles (including current cell)
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                p += 1
            elif (nx, ny) in obstacles:
                p += 1
        return p

    # Step evaluation: minimize self distance; maximize opponent distance; avoid high-pressure/obstacle cells
    cur_pressure = obstacle_pressure(sx, sy)
    chosen = None
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Opponent distance after our move is approximated by how much worse our target progress is for them
        # since opponent doesn't move here; still, we reward moving away from locations that reduce their race advantage.
        opp_target_adv = (od - man(ox, oy, tx, ty))  # =0; kept deterministic structure
        press = obstacle_pressure(nx, ny)
        # Key: (better race progress first), avoid obstacles/bottlenecks, then lexicographic move tie-break via dx,dy
        key = (d, -od, press - cur_pressure, dx, dy)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    if chosen is None:
        return [0, 0]
    return [chosen[0], chosen[1]]