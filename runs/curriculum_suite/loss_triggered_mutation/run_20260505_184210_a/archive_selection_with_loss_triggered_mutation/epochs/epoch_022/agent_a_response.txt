def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h:
                if (rx, ry) not in obs:
                    res.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None  # (score, dx, dy)

    # If no resources known, drift to center while avoiding obstacles
    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            dcent = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            key = (dcent, nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Main heuristic: choose a move that improves our approach while denying opponent access
    # by favoring resources where we can arrive earlier or by pushing opponent away from the nearest
    # "value" resource for both agents.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # center bias to avoid wall-sticking
        dcent = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        # Evaluate best contested target for this move
        best_target_score = None
        for rx, ry in res:
            our_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)

            # Prefer immediate/near-term pickup; deny opponent by increasing their relative advantage.
            # Also mildly encourage moving towards resources that are farther from opponent, even if not closest.
            # Lower is better.
            s = our_d - 0.65 * (opp_d - our_d)
            if our_d == 0:
                s -= 3.0
            # tie-break on closeness to resource, then on how hard it is for opponent to get it
            key = (s, our_d, -opp_d, rx, ry)
            if best_target_score is None or key < best_target_score:
                best_target_score = key

        # Combine target score with center bias (small) and a gentle "squeeze": avoid moving where opponent is very close
        # to the same region by using distance to opponent after move.
        opp_contact = abs(nx - ox) + abs(ny - oy)
        total = (best_target_score[0] + 0.015 * dcent - 0.002 * opp_contact, best_target_score[1], best_target_score[2], dx, dy)
        if best is None or total < best[0]:
            best = (total, dx, dy)

    return [best[1], best[2]] if best else [0, 0]