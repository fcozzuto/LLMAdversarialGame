def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def sqdist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    my_cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            my_cands.append((dx, dy, nx, ny))
    if not my_cands:
        return [0, 0]

    # One-ply minimax: we choose move; opponent responds by moving to maximize distance from us.
    best = None
    best_key = None
    for dx, dy, nx, ny in my_cands:
        # Opponent move options from (ox, oy)
        worst_d = -1
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not inside(tx, ty):
                continue
            d = sqdist(nx, ny, tx, ty)
            if d > worst_d:
                worst_d = d
        # If no legal opponent move (shouldn't happen), treat as current distance.
        if worst_d < 0:
            worst_d = sqdist(nx, ny, ox, oy)

        # Tie-breakers: prefer smaller immediate distance and then alignment (diagonal/axial towards opponent).
        imm_d = sqdist(nx, ny, ox, oy)
        ax = abs(nx - ox)
        ay = abs(ny - oy)
        align_bonus = (ax == 0 or ay == 0)  # axial alignment preferred
        key = (worst_d, imm_d, 0 if align_bonus else 1, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]