def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (man(nx, ny, tx, ty), man(nx, ny, ox, oy), abs(nx - tx) + abs(ny - ty))
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    # Two-layer decision:
    # 1) Prefer moves that reduce the distance advantage to a reachable resource.
    # 2) If no clear advantage, choose move minimizing own distance to the best contested resource.
    best_move = (0, 0)
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        best_adv = -10**9
        best_self = 10**9
        best_contested = None
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            d_opp_after = man(nx, ny, ox, oy)  # proxy to avoid drifting to opponent
            # advantage: self closeness relative to opponent
            adv = (d_opp - d_self) * 10 - d_self
            # slight penalty if it likely opens a path to the opponent nearby
            adv -= max(0, 3 - d_opp_after)
            if adv > best_adv or (adv == best_adv and d_self < best_self):
                best_adv = adv
                best_self = d_self
                best_contested = (rx, ry)

        # Primary: maximize advantage; Secondary: minimize own distance; Tertiary: minimize opponent distance to that same resource.
        rx, ry = best_contested
        opp_to_res = man(ox, oy, rx, ry)
        key = (-best_adv, best_self, opp_to_res, abs(nx - sx) + abs(ny - sy), dx, dy)
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)
    return [best_move[0], best_move[1]]