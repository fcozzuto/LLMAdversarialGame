def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = observation.get("self_role", "pursuer")
    pursuer = (str(self_role).lower() != "evader")

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obs_adj_pen(x, y):
        # Prefer not to be adjacent to obstacles (tames zigzag into walls).
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))
    moves += [(0, 0)]

    best_move = (0, 0)
    best_score = None

    # For deterministic tie-breaking: scan moves in fixed order and compare only score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny)
        adj = obs_adj_pen(nx, ny)

        # Small bias toward center-ish when chasing, toward edges when evading (helps corners).
        cx, cy = w // 2, h // 2
        center_dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        edge_dist = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)

        if pursuer:
            # minimize distance, then avoid obstacle-adjacent positions, then prefer slightly toward center to tighten.
            score = d + 2.0 * adj - 0.02 * center_dist
            better = (best_score is None) or (score < best_score)
        else:
            # maximize distance, then avoid obstacle-adjacent positions, then prefer edges to force capture timing.
            score = -d + 2.0 * adj - 0.3 * edge_dist
            better = (best_score is None) or (score < best_score)

        if better:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]