def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if in_bounds(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break order already fixed by dirs

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no resources, retreat/press based on distance to opponent's corner
    opp_target = (0, 0) if (ox > w // 2) else (w - 1, h - 1)  # deterministic "chase" target-ish

    best = (0, 0, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if resources:
            # Choose move that maximizes advantage for the most contested resource
            best_adv = -10**18
            best_me_dist = 10**18
            for tx, ty in resources:
                dm = manh(nx, ny, tx, ty)
                do = manh(nx, ny, ox, oy)  # not needed directly but keep scale
                # contest: how much closer I am than opponent would be next turn
                do_to_res = manh(ox, oy, tx, ty)
                adv = (do_to_res - dm) * 10
                # prefer closer actual resource even if advantage similar
                key = adv - dm * 1
                if key > best_adv or (key == best_adv and dm < best_me_dist):
                    best_adv = key
                    best_me_dist = dm
            # add small incentive to get away from opponent if we're behind, else move toward them only slightly
            my_to_opp = manh(nx, ny, ox, oy)
            opp_pressure = -my_to_opp * (0.2 if best_adv < 0 else 0.05)
            score = best_adv + opp_pressure
        else:
            # After resources exhausted: head toward own corner mirror to reduce opponent dominance
            tx, ty = opp_target
            score = -manh(nx, ny, tx, ty) - manh(nx, ny, ox, oy) * 0.01

        if score > best[2]:
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]