def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    best = None
    best_score = None

    if unclaimed:
        # Prefer moving into an adjacent unclaimed cell; else toward nearest unclaimed.
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            if (nx, ny) in set(unclaimed):
                score = 10_000 + (abs(nx - ox) + abs(ny - oy)) * 0.001
            else:
                md = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed)
                score = 1000 - md
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
        if best is not None:
            return best

    # Fallback: stay valid, maximize distance from opponent (deterministic order).
    best = [0, 0]
    best_score = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        score = abs(nx - ox) + abs(ny - oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best