def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Evaluate move by (1) best "grab advantage" on resources and (2) distance to opponent.
    best = None
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = (sx, sy) if (dx == 0 and dy == 0) else (sx + dx, sy + dy)
            if not inb(nx, ny):
                continue

            # Grab advantage: prefer moving toward resources where we are closer than opponent.
            grab = -10**9
            if resources:
                for r in resources:
                    if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                        continue
                    rx, ry = r[0], r[1]
                    if not inb(rx, ry):
                        continue
                    ds = man(nx, ny, rx, ry)
                    do = man(ox, oy, rx, ry)
                    adv = do - ds  # positive means we are closer than opponent from their current position
                    # Encourage approaching the most contestable / nearest favorable resource.
                    score = adv * 3 - ds
                    if score > grab:
                        grab = score
            else:
                grab = -10

            # Opponent pressure: keep distance modestly, but don't turtle over grabbing.
            dop_next = man(nx, ny, ox, oy)
            opp_term = dop_next * 0.2

            score = grab + opp_term
            if score > best_score:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]