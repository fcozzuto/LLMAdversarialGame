def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((x, y) for x, y in obstacles)
    if not resources:
        tx, ty = (w // 2), (h // 2)
        best = None
        bestd = 10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    d = abs(nx - tx) + abs(ny - ty)
                    if d < bestd:
                        bestd = d
                        best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked_penalty(nx, ny, tx, ty):
        # Favor moves that don't immediately step into congestion near obstacles
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                mx, my = nx + ax, ny + ay
                if 0 <= mx < w and 0 <= my < h and (mx, my) in obs:
                    p += 0.5
        # Slightly bias toward reducing distance
        return p + 0.1 * dist(nx, ny, tx, ty)

    # Target selection: prefer resources where we're meaningfully closer than opponent
    best_t = None
    best_sc = -10**9
    for rx, ry in resources:
        d_me = dist(sx, sy, rx, ry)
        d_op = dist(ox, oy, rx, ry)
        sc = (d_op - d_me) * 10 - d_me
        # If obstacle near our path, downweight a bit by one-step check from current position
        if (rx, ry) in obs:
            sc -= 1000
        # Deterministic secondary preference: toward higher coordinates sum (break ties)
        sc += 0.001 * (rx + ry)
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    tx, ty = best_t
    # Move choice: deterministic greedy to reduce distance to target, with obstacle avoidance
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                # If that resource is nearby, also try to deny opponent by not moving into their likely approach
                d_now = dist(nx, ny, tx, ty)
                d_op_to_target = dist(ox, oy, tx, ty)
                # Mild deny: if we move away while opponent is close, penalize
                denom = (d_op_to_target + 1)
                deny = 0.0
                if d_me := dist(sx, sy, tx, ty):
                    if denom <= 6 and d_now > d_me:
                        deny += 5.0 * (d_now - d_me)
                moves.append((d_now + blocked_penalty(nx, ny, tx, ty) + deny, dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    # Deterministic tie-break: sort by score, then dx, then dy, then position
    moves.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    _, dx, dy, _, _ = moves[0]
    return [int(dx), int(dy)]