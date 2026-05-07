def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    def cell_score(x, y):
        best_adv = -10**9
        nearest_r = 10**9
        nearest_opp = 10**9
        for rx, ry in resources:
            ds = abs(rx - x) + abs(ry - y)
            do = abs(rx - ox) + abs(ry - oy)
            adv = do - ds  # positive means we are closer than opponent
            if adv > best_adv:
                best_adv = adv
            if ds < nearest_r:
                nearest_r = ds
        nearest_opp = abs(x - ox) + abs(y - oy)
        # Objective: maximize winning advantage; if equal, grab closer resource; otherwise avoid approaching opponent too much.
        return (best_adv * 1000) - (nearest_r * 3) - (nearest_opp * 0.8)

    # Meaningful change from pure resource-chasing: pick move that maximizes advantage against opponent (not just closeness).
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = cell_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    if best_val == -10**18:
        return [0, 0]
    return best_move