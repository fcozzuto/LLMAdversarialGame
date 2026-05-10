def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = None

    # Evaluation: pick a move that creates the biggest "win margin" over the opponent
    # across all remaining resources, with a strong bias toward resources we can beat.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_best = 10**9
        opp_best = 10**9
        val = 0.0

        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            my_best = ds if ds < my_best else my_best
            opp_best = do if do < opp_best else opp_best

            # Win margin on this resource: positive if we are closer (so we can "race" them).
            margin = do - ds
            if margin > 0:
                val += 8.0 + 1.0 * margin  # strong if we can beat them
                # Slightly prioritize resources on/near opponent's current row to prevent their sweep.
                val += 0.25 if ry == oy else 0.0
            elif margin == 0:
                val += 2.0  # contested
                val += 0.05 if ry == oy else 0.0
            else:
                # If we're behind, still add small value for reducing their eventual capture time.
                val -= 0.35 * (-margin)

            # Small preference to immediate collection / proximity (ties broken by this).
            val += 0.02 * (-ds)

        # If we are currently able to take something quickly, favor it.
        val += -0.03 * my_best
        # If the opponent is currently very close to some resource, try to counter by racing.
        val += 0.01 * opp_best

        key = (-val, dx, dy)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]