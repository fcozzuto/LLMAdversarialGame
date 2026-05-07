def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Deterministic drift to break symmetry: head to upper-left toward your quadrant.
        tx, ty = max(0, (w // 2) - 1), max(0, (h // 2) - 1)
        best = (10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = md(nx, ny, tx, ty)
            if v < best[0] or (v == best[0] and (dx, dy) < (best[1], best[2])):
                best = (v, dx, dy)
        return [best[1], best[2]] if best[1] != 0 or best[2] != 0 else [0, 0]

    # Choose move that maximizes contest value for best reachable resource, not just lead.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            selfd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)

            # If we can arrive no later than opponent, strongly prefer (resource grabbing).
            if selfd <= oppd:
                score = 200 - selfd + (oppd - selfd) * 3
            else:
                # If we are behind, prefer minimizing the "race" gap (contesting against denier).
                score = (oppd - selfd) * 2 - selfd * 0.5 - (selfd - oppd) * 0.1

            # Tiny deterministic tie-breaker toward central-ish cells (reduces dithering).
            score -= (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)) * 0.01

            if score > val:
                val = score
        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]