def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    if not resources:
        return [0, 0]

    targets = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = abs(rx - x) + abs(ry - y)
        od = abs(rx - ox) + abs(ry - oy)
        # Prefer resources where we are closer (or opponent is farther); then closer overall.
        # Deterministic tie-break by coordinates.
        targets.append((md - od, md, rx, ry))
    if not targets:
        return [0, 0]
    _, _, tx, ty = min(targets)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    opp_base = abs(tx - ox) + abs(ty - oy)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)  # opponent doesn't move now; keep bias only via our choice
        # Secondary tie-break: step closer to target; tertiary: avoid moving away from best target.
        # Add deterministic preference: prioritize smaller dx, then dy.
        key = (my_d, -(opp_base - opp_d), nx, ny, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]