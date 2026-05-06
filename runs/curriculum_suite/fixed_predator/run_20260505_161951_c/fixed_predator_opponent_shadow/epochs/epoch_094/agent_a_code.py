def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (md(nx, ny, tx, ty), md(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_key = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        opp_dist = md(nx, ny, ox, oy)

        max_adv = None
        best_self_d = None
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - self_d
            if max_adv is None or adv > max_adv or (adv == max_adv and self_d < best_self_d):
                max_adv = adv
                best_self_d = self_d

        # Primary: maximize advantage over opponent to some resource.
        # Secondary: get closer to that winning resource.
        # Tertiary: keep distance from opponent.
        key = (max_adv, -best_self_d, opp_dist)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]