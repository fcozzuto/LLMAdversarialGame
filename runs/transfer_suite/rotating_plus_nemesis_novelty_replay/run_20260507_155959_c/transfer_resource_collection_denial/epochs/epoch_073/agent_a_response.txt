def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (dx, dy) == (0, 0):
            valid.append((0, 0))
        elif inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if resources:
        best_score = None
        best_move = (0, 0)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            my_step = 0 if (dx == 0 and dy == 0) else 1
            # Choose a resource to "win": self arrival sooner than opponent (tie-break: closer)
            chosen = None
            chosen_val = None
            for rx, ry in resources:
                if not (0 <= rx < w and 0 <= ry < h):
                    continue
                md = max(abs(rx - nx), abs(ry - ny))  # king-move distance
                od = max(abs(rx - ox), abs(ry - oy))
                # Larger is better: (opponent delay) then closeness after intercept
                score = (od - md, -md)
                if chosen_val is None or score > chosen_val:
                    chosen_val = score
                    chosen = (rx, ry)
            if chosen is None:
                continue
            rx, ry = chosen
            md = max(abs(rx - nx), abs(ry - ny))
            od = max(abs(rx - ox), abs(ry - oy))
            # Encourage actions that improve margin; small bias to reduce distance
            final_score = (od - md, -md, -(abs(ox - nx) + abs(oy - ny)), -my_step)
            if best_score is None or final_score > best_score:
                best_score = final_score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No visible resources: move toward center, but prefer staying closer to the line away from opponent
    cx, cy = w // 2, h // 2
    best = None
    best_move = (0, 0)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        score = (-(abs(nx - cx) + abs(ny - cy)), -(abs(nx - ox) + abs(ny - oy)), -max(abs(dx), abs(dy)))
        if best is None or score > best:
            best = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]