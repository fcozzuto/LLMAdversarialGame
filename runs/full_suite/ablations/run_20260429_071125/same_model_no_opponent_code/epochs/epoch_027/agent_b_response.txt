def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if (sx, sy) in resources:
        return [0, 0]

    if resources:
        best_t = None
        best_d = 10**9
        for tx, ty in resources:
            d = max(abs(tx - sx), abs(ty - sy))  # Chebyshev for 8-dir
            if d < best_d or (d == best_d and (tx, ty) < (best_t[0], best_t[1])):
                best_d = d
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        d_t = max(abs(tx - nx), abs(ty - ny))
        if resources and (nx, ny) in resources:
            score = -10**7 + d_t
        else:
            d_o = max(abs(ox - nx), abs(oy - ny))
            # Prefer getting closer to target, avoid moving adjacent to opponent.
            score = d_t * 1000 + (0 if resources else 1) * 10 + (10 if d_o <= 1 else 0) * (5 - d_o)

        if score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]