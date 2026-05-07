def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def pt(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return int(p[0]), int(p[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        x, y = pt(p)
        if inb(x, y):
            obst.add((x, y))

    resources = [pt(r) for r in (observation.get("resources") or [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    def man(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx + dy

    # Prefer moves that maximize being closer to some resource than the opponent (denial when possible).
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        local_best_adv = -10**9
        local_best_sd = 10**9
        for rx, ry in resources:
            dS = man(nx, ny, rx, ry)
            dO = man(ox, oy, rx, ry)
            adv = dO - dS  # positive => we are closer
            # Capture best advantage; then prefer smaller self-distance among same advantage.
            if adv > local_best_adv or (adv == local_best_adv and dS < local_best_sd):
                local_best_adv = adv
                local_best_sd = dS

        # Convert into a move score. Heavily reward positive advantage; otherwise minimize our distance.
        score = (local_best_adv * 1000) - local_best_sd
        # Tie-break deterministically: prefer closer to center if same score, else fixed move order.
        center_bias = abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2)
        key = (score, -local_best_sd, -local_best_adv, -(-center_bias))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]