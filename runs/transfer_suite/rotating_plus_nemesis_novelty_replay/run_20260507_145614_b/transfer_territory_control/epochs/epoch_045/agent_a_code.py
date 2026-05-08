def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p[:2]) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p[:2]) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)
    selfT = set(tuple(p[:2]) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    oppT = set(tuple(p[:2]) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    move_options = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = None

    # Heuristic: take/expand territory on our side; prefer unclaimed; punish stepping into opponent only if it stalls.
    chase = 1 if (observation.get("self_territory_count", 0) >= observation.get("opponent_territory_count", 0)) else 0

    for dx, dy in move_options:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in selfT:
            score += 2
        elif (nx, ny) in unclaimed:
            score += 6
        elif (nx, ny) in oppT:
            score += 7  # flipping on entry enabled
            if chase:
                score += 1
        else:
            score += 0

        # Move toward our chosen corner; if we're behind, also reduce distance to opponent territory for capture opportunities.
        score += -2 * (abs(nx - tx) + abs(ny - ty))
        if not chase:
            score += 1 * (-(abs(nx - ox) + abs(ny - oy)))

        # Mild penalty for being adjacent to obstacles to reduce collision risk deterministically.
        score += -0.2 * sum(1 for ax, ay in [(nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1), (nx - 1, ny - 1), (nx - 1, ny + 1), (nx + 1, ny - 1), (nx + 1, ny + 1)] if (ax, ay) in obstacles)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]