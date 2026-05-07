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

    # If no visible resources, head to center while avoiding obstacles
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                sc = -(abs(nx - cx) + abs(ny - cy))
                if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
                    best = (sc, (dx, dy))
        if best is None:
            return [0, 0]
        return [best[1][0], best[1][1]]

    # Evaluate each possible next move by best "resource advantage"
    # Advantage: opp_distance - self_distance (prefer resources where we are closer)
    # If opponent position unknown, just minimize self distance.
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue

            if opp_exists:
                best_adv = -10**18
                for rx, ry in resources:
                    sd = abs(rx - nx) + abs(ry - ny)
                    od = abs(rx - ox) + abs(ry - oy)
                    adv = od - sd
                    # small penalty for longer path even if advantage similar
                    cand = adv * 10 - sd
                    if cand > best_adv:
                        best_adv = cand
                sc = best_adv
            else:
                # Just go to nearest resource
                best_sd = 10**18
                for rx, ry in resources:
                    sd = abs(rx - nx) + abs(ry - ny)
                    if sd < best_sd:
                        best_sd = sd
                sc = -best_sd

            if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
                best = (sc, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]