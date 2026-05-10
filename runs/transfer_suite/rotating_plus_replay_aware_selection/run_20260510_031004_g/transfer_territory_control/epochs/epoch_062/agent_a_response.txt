def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    unclaimed = observation.get("unclaimed_cells", []) or []
    opp_terr = observation.get("opponent_territory", []) or []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def center_dist(p):
        return abs(p[0] - cx) + abs(p[1] - cy)

    def pick_target():
        if unclaimed:
            best = None
            for tx, ty in unclaimed:
                if not inb(tx, ty) or (tx, ty) in obstacles:
                    continue
                ds = abs(tx - sx) + abs(ty - sy)
                do = abs(tx - ox) + abs(ty - oy)
                # Prefer closer to us, but also closer to center and not too close to opponent.
                key = (ds, center_dist((tx, ty)), -do)
                if best is None or key < best[0]:
                    best = (key, (tx, ty))
            if best is not None:
                return best[1]
        if opp_terr:
            best = None
            for tx, ty in opp_terr:
                if not inb(tx, ty) or (tx, ty) in obstacles:
                    continue
                ds = abs(tx - sx) + abs(ty - sy)
                key = (ds, center_dist((tx, ty)))
                if best is None or key < best[0]:
                    best = (key, (tx, ty))
            if best is not None:
                return best[1]
        # Final fallback: head to center
        return (int(round(cx)), int(round(cy)))

    tx, ty = pick_target()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        ds_before = abs(sx - tx) + abs(sy - ty)
        ds_after = abs(nx - tx) + abs(ny - ty)
        move_gain = ds_before - ds_after

        # Small tie-breaks: push toward center, and avoid stepping away from center if gains tie.
        dc_before = abs(sx - cx) + abs(sy - cy)
        dc_after = abs(nx - cx) + abs(ny - cy)
        center_gain = dc_before - dc_after

        # Deterministic penalty if move goes adjacent to opponent territory's nearest point (can be risky).
        opp_adj_pen = 0
        if opp_terr:
            # Only check a few nearest-ish by deterministic sampling: consider at most 8 points.
            # (Still deterministic due to fixed iteration order.)
            k = 0
            for px, py in opp_terr:
                if k >= 8:
                    break
                if abs(px - nx) + abs(py - ny) == 1:
                    opp_adj_pen = 1
                    break
                k += 1

        score = (move_gain, center_gain, -opp_adj_pen, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]