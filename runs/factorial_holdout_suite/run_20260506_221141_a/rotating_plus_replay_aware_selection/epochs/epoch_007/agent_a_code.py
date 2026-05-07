def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            dirs.append((dx, dy))
    if not dirs:
        return [0, 0]

    if not resources:
        # Keep a mild bias to move toward the center so we don't get stuck.
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            val = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if best is None or val > best[0] or (val == best[0] and (nx, ny) < best[1]):
                best = (val, (nx, ny))
        return [best[1][0] - x, best[1][1] - y]

    # Evaluate each move by choosing the target resource we would capture "earlier",
    # then break ties by safety (difference in distance vs opponent) and finish distance.
    # Use Manhattan distances as a fast heuristic (consistent/deterministic).
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        move_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = abs(rx - nx) + abs(ry - ny)
            opd = abs(rx - ox) + abs(ry - oy)

            # Prefer states where we are closer than opponent to the same resource.
            # If equal, prefer finishing sooner; if still tied, prefer deterministic coord order.
            earlier_margin = opd - myd  # higher means we are earlier
            val = (earlier_margin, -myd, -(rx + 31 * ry))
            if move_best is None or val > move_best:
                move_best = val

        # Additional anti-blocking: if a move increases our nearest resource distance, penalize.
        cur_near = min((abs(rx - x) + abs(ry - y) for rx, ry in resources if (rx, ry) not in obstacles), default=10**9)
        new_near = min((abs(rx - nx) + abs(ry - ny) for rx, ry in resources if (rx, ry) not in obstacles), default=10**9)
        penalty = new_near - cur_near  # prefer <=0
        score = (move_best[0] if move_best else -10**9, move_best[1] if move_best else -10**9, -penalty, -(nx + 97 * ny))

        if best_val is None or score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]