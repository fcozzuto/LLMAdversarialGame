def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -(abs(nx - cx) + abs(ny - cy))
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if opp_exists:
            # Prefer moves that make us closer to a resource than the opponent.
            primary = -10**18
            secondary = 10**18
            for rx, ry in resources:
                our_d = abs(nx - rx) + abs(ny - ry)
                opp_d = abs(ox - rx) + abs(oy - ry)
                diff = opp_d - our_d
                if diff > primary or (diff == primary and our_d < secondary):
                    primary, secondary = diff, our_d
            sc = (primary * 1000) - secondary
        else:
            # No opponent info: just go toward the nearest resource.
            our_d, _ = min((abs(nx - rx) + abs(ny - ry), (rx, ry)) for rx, ry in resources)
            sc = -our_d
        if sc > best[0]:
            best = (sc, dx, dy)
    return [best[1], best[2]]